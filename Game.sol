// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import "@chainlink/contracts/src/v0.8/ConfirmedOwner.sol";
import "@chainlink/contracts/src/v0.8/interfaces/KeeperCompatibleInterface.sol";

error Game__NotEnoughETHEntered();
error Game__TransferFailed();
error Game__NotOpen();
error Game__UpKeepNotNeeded(
    uint256 currentBalance,
    uint256 numPlayers,
    uint256 GameState
);

contract Game is KeeperCompatibleInterface, ChainlinkClient, ConfirmedOwner {
    enum GameState {
        OPEN,
        CALCULATING,
        FINISHED
    }

    uint256 private immutable i_entranceFee;
    address payable[] private s_players;
    uint256 private s_reward;
    address private s_lastCaller;
    uint256 private s_initiation = block.timestamp;
    GameState private s_gameState;
    uint256 private immutable i_timeLimit;
    bytes32 private s_jobId;
    uint256 private s_fee;
    address private s_owner;

    /**Events */
    event gameEnter(address indexed player);
    event dataPush(address indexed player);
    event dataPushSuccessful(address indexed player);
    event stakeReturned(address indexed player);

    constructor(
        uint256 entranceFee,
        uint256 timeLimit,
        uint256 fundingAmount
    ) ConfirmedOwner(msg.sender) {
        setChainlinkToken(0x779877A7B0D9E8603169DdbD7836e478b4624789);
        setChainlinkOracle(0x6090149792dAAeE9D1D568c9f9a6F6B46AA29eFD);
        s_jobId = "ca98366cc7314957b8c012c72f05aeeb";
        s_fee = (1 * LINK_DIVISIBILITY) / 10; // 0,1 * 10**18 (Varies by network and job)
        i_entranceFee = entranceFee;
        s_gameState = GameState.OPEN;
        s_gameState = GameState(0);
        s_initiation = block.timestamp;
        i_timeLimit = timeLimit;
        s_owner = payable(msg.sender);
        require(msg.value == fundingAmount, "Insufficient funding amount");
    }

    function checkUpkeep(
        bytes memory /*checkData*/ //changed from external to public to allow calling from within the SC
    )
        public
        view
        override
        returns (bool upkeepNeeded, bytes memory /*performData */)
    {
        bool isOpen = (s_gameState == GameState.OPEN);
        bool timePassed = ((block.timestamp - s_initiation) > i_timeLimit);
        bool hasPlayers = (s_players.length > 0);
        bool hasETH = (address(this).balance > 0);
        upkeepNeeded = (isOpen && timePassed && hasPlayers && hasETH);
        return (upkeepNeeded, "0x0");
    }

    function performUpkeep(bytes calldata /* performData */) external override {
        (bool upkeepNeeded, ) = checkUpkeep("");
        if (!upkeepNeeded) {
            revert Game__UpKeepNotNeeded(
                address(this).balance,
                s_players.length,
                uint256(s_gameState)
            );
        }
        s_gameState = GameState.CALCULATING;
        s_reward = address(this).balance;
        Chainlink.Request memory req = buildChainlinkRequest(
            s_jobId,
            address(this),
            this.fulfill.selector
        );
        req.add("get", "api/generateReward");
        req.add("path", "res");
        req.addInt("times", 1);
        return sendChainlinkRequest(req, s_fee);
        emit dataPush(msg.sender);
    }

    function enterGame() public payable returns (uint256) {
        if (s_gameState != GameState.OPEN) {
            revert Game__NotOpen();
        }
        s_players.push(payable(msg.sender));
        emit gameEnter(msg.sender);
        return s_players.length - 1;
    }

    function enterData(uint256 index, string memory str) public payable {
        if (msg.value < i_entranceFee) {
            revert Game__NotEnoughETHEntered();
        }
        if (s_gameState != GameState.OPEN) {
            revert Game__NotOpen();
        }
        Chainlink.Request memory req = buildChainlinkRequest(
            s_jobId,
            address(this),
            this.fulfill.selector
        );
        req.add("post", "api/data");
        req.add("body", str);
        req.add("path", "res");
        req.addInt("times", 1);

        return sendChainlinkRequest(req, s_fee);
        emit dataPush(msg.sender);
    }

    function getReward(uint256 index) public payable {
        if (s_gameState != GameState.FINISHED) {
            revert Game__NotOpen();
        }
        s_lastCaller = msg.sender;
        Chainlink.Request memory req = buildChainlinkRequest(
            s_jobId,
            address(this),
            this.fulfill.selector
        );
        req.add("post", "api/getReward");
        req.add("body", index);
        req.add("path", "res");
        req.addInt("times", 10 ** 8);

        return sendChainlinkRequest(req, s_fee);
        emit dataPush(msg.sender);
    }

    function fulfill(
        bytes32 _requestId,
        uint256 _result
    ) public recordChainlinkFulfillment(_requestId) {
        if (_result > 0) {
            (bool success, ) = s_lastCaller.call{
                value: (_result * s_reward) / (10 ** 8)
            }("");
            if (!success) revert Game__TransferFailed();
            emit stakeReturned(s_lastCaller);
        }
    }

    function getEntranceFee() public view returns (uint256) {
        return i_entranceFee;
    }

    function getPlayer(uint256 index) public view returns (address) {
        return s_players[index];
    }

    function getGameState() public view returns (uint256) {
        return uint256(s_gameState);
    }

    function getNumPlayers() public view returns (uint256) {
        return (s_players.length);
    }

    function getTimeLimit() public view returns (uint256) {
        return i_timeLimit;
    }
}
