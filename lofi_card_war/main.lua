--[[
Lofi Card War - A Love2D Game
Based on War, with RPG classes and items.
]]

-- ========================================
-- Configuration & Constants
-- ========================================
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

CARD_WIDTH = 70
CARD_HEIGHT = 100
CARD_PADDING = 10

-- RPG Classes
CLASSES = {"Warrior", "Thief", "Mage"}
-- Class advantages: Key beats Value
CLASS_ADVANTAGES = {
    Warrior = "Thief",
    Thief = "Mage",
    Mage = "Warrior"
}

-- Suits and Ranks (like a standard deck)
SUITS = {"Swords", "Daggers", "Scrolls", "Hammers"} -- Themed suits
RANKS = {"2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"}
RANK_VALUES = {
    ["2"]=2, ["3"]=3, ["4"]=4, ["5"]=5, ["6"]=6, ["7"]=7, ["8"]=8, ["9"]=9, ["10"]=10,
    ["J"]=11, ["Q"]=12, ["K"]=13, ["A"]=14
}

-- Game States
GAME_STATE = "loading" -- loading, menu, playing, war, gameover

-- ========================================
-- Global Variables
-- ========================================
playerDeck = {}
opponentDeck = {}
playerCard = nil     -- Card currently revealed by player
opponentCard = nil   -- Card currently revealed by opponent
playerItem = nil     -- Player's current item modifier
opponentItem = nil   -- Opponent's current item modifier
warPile = {}         -- Cards currently in the "war" pot
message = "Lofi Card War - Press Space to Start"
winner = nil         -- "player" or "opponent" or nil
gameFont = nil

-- Placeholder for potential items
ITEMS = {
    {name="Rusty Sword", modifier=1, description="+1 Atk"},
    {name="Leather Cap", modifier=1, description="+1 Def"}, -- Def might not be used directly, modifier is generic
    {name="Minor Mana Potion", modifier=1, description="+1 Power"},
    {name="Sharpened Dagger", modifier=2, description="+2 Atk"},
    {name="Enchanted Robe", modifier=2, description="+2 Power"},
    {name="Steel Shield", modifier=2, description="+2 Def"},
}

-- ========================================
-- Helper Functions
-- ========================================

-- Shuffle a table in-place using Fisher-Yates
function shuffle(tbl)
    for i = #tbl, 2, -1 do
        local j = love.math.random(i)
        tbl[i], tbl[j] = tbl[j], tbl[i]
    end
    return tbl
end

-- Create a full deck of cards
function createDeck()
    local deck = {}
    local classIndex = 1
    for _, suit in ipairs(SUITS) do
        for _, rank in ipairs(RANKS) do
            local card = {
                suit = suit,
                rank = rank,
                value = RANK_VALUES[rank],
                -- Assign classes somewhat cyclically based on suit for variety
                class = CLASSES[classIndex]
            }
            table.insert(deck, card)
        end
        -- Cycle through classes (Warrior, Thief, Mage, Warrior again for Hammers)
        classIndex = (classIndex % #CLASSES) + 1
        if classIndex > #CLASSES then classIndex = 1 end -- Ensure it cycles correctly
    end
    return deck
end

-- Deal cards from a source deck to player and opponent
function dealCards(sourceDeck)
    local pDeck = {}
    local oDeck = {}
    for i, card in ipairs(sourceDeck) do
        if i % 2 == 1 then
            table.insert(pDeck, card)
        else
            table.insert(oDeck, card)
        end
    end
    return pDeck, oDeck
end

-- Get a simple string representation of a card
function getCardString(card)
    if not card then return "[No Card]" end
    return string.format("%s of %s (%s)", card.rank, card.suit, card.class:sub(1,1))
end

-- Get a string for an item
function getItemString(item)
    if not item then return "[No Item]" end
    return string.format("%s (%+d)", item.name, item.modifier)
end

-- Calculate the effective value of a card considering class advantages and items
function calculateEffectiveValue(card, opponentCardClass, item)
    if not card then return 0 end

    local baseValue = card.value
    local classBonus = 0
    local itemBonus = 0

    -- Apply class advantage bonus
    if opponentCardClass and CLASS_ADVANTAGES[card.class] == opponentCardClass then
        classBonus = 3 -- Assign a significant bonus for having the advantage
        -- print(card.class .. " beats " .. opponentCardClass .. " -> +3")
    end

    -- Apply item bonus
    if item then
        itemBonus = item.modifier
        -- print("Item bonus: " .. itemBonus)
    end

    return baseValue + classBonus + itemBonus
end

-- Award a random item (simple version)
function awardRandomItem()
    if #ITEMS > 0 then
        local randomIndex = love.math.random(#ITEMS)
        -- Return a copy so modifying it doesn't change the original template
        local itemCopy = {}
        for k, v in pairs(ITEMS[randomIndex]) do
            itemCopy[k] = v
        end
        return itemCopy
    end
    return nil
end

-- ========================================
-- Love2D Callbacks
-- ========================================

function love.load()
    love.window.setTitle("Lofi Card War")
    love.window.setMode(WINDOW_WIDTH, WINDOW_HEIGHT)
    love.graphics.setBackgroundColor(0.1, 0.1, 0.15) -- Dark Lofi background

    -- Load a simple font (replace 'path/to/font.ttf' if you have one, otherwise use default)
    -- Download a free pixel font like 'Press Start 2P' or 'm5x7' for a better lofi feel
    local success
    success, gameFont = pcall(love.graphics.newFont, 20) -- Default font size 20
    if not success or not gameFont then
       print("Warning: Default font not found or failed to load. Using fallback.")
       gameFont = love.graphics.newFont(12) -- Use built-in font as fallback
    end
     if gameFont then love.graphics.setFont(gameFont) end

    math.randomseed(os.time()) -- Seed RNG

    GAME_STATE = "menu" -- Start at the menu
end

function love.update(dt)
    -- Game logic updates based on state
    if GAME_STATE == "playing" then
        -- In this state, we wait for player input (space) to trigger the next comparison
        -- Check for win/loss conditions after a round resolves
        if #playerDeck == 0 and playerCard == nil and #warPile == 0 then
            winner = "opponent"
            message = "Opponent wins! Press R to restart."
            GAME_STATE = "gameover"
        elseif #opponentDeck == 0 and opponentCard == nil and #warPile == 0 then
            winner = "player"
            message = "Player wins! Press R to restart."
            GAME_STATE = "gameover"
        end

    elseif GAME_STATE == "war" then
         -- War state logic - also waits for player input to resolve
          if #playerDeck < 2 then -- Not enough cards for war stakes + next card
            winner = "opponent"
            message = "Player can't continue war! Opponent wins! Press R."
            GAME_STATE = "gameover"
         elseif #opponentDeck < 2 then
            winner = "player"
            message = "Opponent can't continue war! Player wins! Press R."
            GAME_STATE = "gameover"
         end
    end
end

function love.draw()
    -- Clear background
    love.graphics.clear(love.graphics.getBackgroundColor())

    -- Set font if loaded
    if gameFont then love.graphics.setFont(gameFont) end
    love.graphics.setColor(1, 1, 1) -- White text

    -- Draw based on game state
    if GAME_STATE == "menu" then
        love.graphics.printf(message, 0, WINDOW_HEIGHT / 2 - 20, WINDOW_WIDTH, "center")
    elseif GAME_STATE == "playing" or GAME_STATE == "war" or GAME_STATE == "gameover" then
        -- Draw Player Area
        love.graphics.print("Player Deck: " .. #playerDeck, 10, 10)
        love.graphics.print("Item: " .. getItemString(playerItem), 10, 35)
        if playerCard then
            drawCard(playerCard, WINDOW_WIDTH / 2 - CARD_WIDTH - CARD_PADDING, WINDOW_HEIGHT / 2 - CARD_HEIGHT / 2)
        else
            drawCardBack(WINDOW_WIDTH / 2 - CARD_WIDTH - CARD_PADDING, WINDOW_HEIGHT / 2 - CARD_HEIGHT / 2, #playerDeck)
        end

        -- Draw Opponent Area
        love.graphics.print("Opponent Deck: " .. #opponentDeck, WINDOW_WIDTH - 160, 10)
         love.graphics.print("Item: " .. getItemString(opponentItem), WINDOW_WIDTH - 250, 35) -- Adjust position
        if opponentCard then
            drawCard(opponentCard, WINDOW_WIDTH / 2 + CARD_PADDING, WINDOW_HEIGHT / 2 - CARD_HEIGHT / 2)
        else
            drawCardBack(WINDOW_WIDTH / 2 + CARD_PADDING, WINDOW_HEIGHT / 2 - CARD_HEIGHT / 2, #opponentDeck)
        end

        -- Draw War Pile Indicator
        if #warPile > 0 then
             love.graphics.print("War Pile: " .. #warPile, WINDOW_WIDTH / 2 - 50, WINDOW_HEIGHT / 2 + CARD_HEIGHT / 2 + 20)
        end

        -- Draw Message Bar
        love.graphics.printf(message, 0, WINDOW_HEIGHT - 50, WINDOW_WIDTH, "center")
    end
end

-- Function to draw a card representation (simple text for lofi)
function drawCard(card, x, y)
    if not card then return end
    love.graphics.setColor(0.8, 0.8, 0.7) -- Light grey card color
    love.graphics.rectangle("fill", x, y, CARD_WIDTH, CARD_HEIGHT, 5, 5) -- Rounded corners

    love.graphics.setColor(0.1, 0.1, 0.15) -- Dark text
    love.graphics.printf(card.rank, x, y + 5, CARD_WIDTH, "center")
    love.graphics.printf(card.suit:sub(1,3), x, y + 30, CARD_WIDTH, "center")
    love.graphics.printf(card.class:sub(1,1), x, y + 55, CARD_WIDTH, "center") -- Class initial
    love.graphics.printf(tostring(card.value), x, y + CARD_HEIGHT - 25, CARD_WIDTH, "center") -- Base value
end

-- Function to draw a card back
function drawCardBack(x, y, count)
     love.graphics.setColor(0.4, 0.2, 0.3) -- Dark purple/red back
     love.graphics.rectangle("fill", x, y, CARD_WIDTH, CARD_HEIGHT, 5, 5)
     love.graphics.setColor(0.9, 0.9, 0.8)
     love.graphics.printf("?", x, y + CARD_HEIGHT/2 - 10, CARD_WIDTH, "center")
     -- Optionally display card count on the back
     love.graphics.printf(tostring(count), x, y + 5, CARD_WIDTH, "center")
end

-- ========================================
-- Game Logic Functions
-- ========================================

function startGame()
    local fullDeck = createDeck()
    fullDeck = shuffle(fullDeck)
    playerDeck, opponentDeck = dealCards(fullDeck)
    playerCard = nil
    opponentCard = nil
    playerItem = nil -- Reset items
    opponentItem = nil
    warPile = {}
    winner = nil
    message = "Press Space to draw!"
    GAME_STATE = "playing"
end

function playRound()
    if GAME_STATE ~= "playing" then return end -- Only play if in the right state
    if #playerDeck == 0 or #opponentDeck == 0 then return end -- Need cards to play

    -- 1. Draw cards
    playerCard = table.remove(playerDeck, 1)
    opponentCard = table.remove(opponentDeck, 1)
    table.insert(warPile, playerCard)     -- Add cards to pot immediately
    table.insert(warPile, opponentCard)

    -- 2. Calculate effective values
    local playerEffValue = calculateEffectiveValue(playerCard, opponentCard.class, playerItem)
    local opponentEffValue = calculateEffectiveValue(opponentCard, playerCard.class, opponentItem)

    -- 3. Compare and determine winner
    if playerEffValue > opponentEffValue then
        -- Player wins round
        message = string.format("Player wins round! %s (%d) vs %s (%d). Press Space.",
                                getCardString(playerCard), playerEffValue,
                                getCardString(opponentCard), opponentEffValue)
        -- Add war pile cards to bottom of player deck
        for _, card in ipairs(warPile) do
            table.insert(playerDeck, card)
        end
        warPile = {} -- Clear war pile
        -- Reset revealed cards for next round (they are now in the deck)
        playerCard = nil
        opponentCard = nil
        GAME_STATE = "playing" -- Ready for next input

    elseif opponentEffValue > playerEffValue then
        -- Opponent wins round
        message = string.format("Opponent wins round! %s (%d) vs %s (%d). Press Space.",
                                getCardString(playerCard), playerEffValue,
                                getCardString(opponentCard), opponentEffValue)
        -- Add war pile cards to bottom of opponent deck
        for _, card in ipairs(warPile) do
            table.insert(opponentDeck, card)
        end
        warPile = {} -- Clear war pile
        playerCard = nil
        opponentCard = nil
        GAME_STATE = "playing" -- Ready for next input

    else
        -- Tie! Go to War
        message = string.format("WAR! %s (%d) ties %s (%d). Press Space for War!",
                                getCardString(playerCard), playerEffValue,
                                getCardString(opponentCard), opponentEffValue)
        GAME_STATE = "war"
        -- Cards stay revealed, pile stays as is until war resolves
    end
end

function resolveWar()
    if GAME_STATE ~= "war" then return end

    -- Check if players have enough cards for the stake (1 face down + 1 face up)
    if #playerDeck < 2 then
        message = "Player doesn't have enough cards for War! Opponent wins the game. Press R."
        winner = "opponent"
        GAME_STATE = "gameover"
        -- Give opponent all remaining cards (optional, but clarifies win)
        for _, card in ipairs(warPile) do table.insert(opponentDeck, card) end
        for _, card in ipairs(playerDeck) do table.insert(opponentDeck, card) end
        playerDeck = {}
        warPile = {}
        playerCard = nil
        opponentCard = nil
        return
    end
    if #opponentDeck < 2 then
         message = "Opponent doesn't have enough cards for War! Player wins the game. Press R."
         winner = "player"
         GAME_STATE = "gameover"
         for _, card in ipairs(warPile) do table.insert(playerDeck, card) end
         for _, card in ipairs(opponentDeck) do table.insert(playerDeck, card) end
         opponentDeck = {}
         warPile = {}
         playerCard = nil
         opponentCard = nil
         return
    end

    -- 1. Place stake (one card face down from each player)
    local playerStake = table.remove(playerDeck, 1)
    local opponentStake = table.remove(opponentDeck, 1)
    table.insert(warPile, playerStake)
    table.insert(warPile, opponentStake)
    message = "Stake placed (" .. #warPile .. " cards). Press Space for final draw!"

    -- 2. Draw face-up cards for comparison
    playerCard = table.remove(playerDeck, 1)
    opponentCard = table.remove(opponentDeck, 1)
    table.insert(warPile, playerCard)
    table.insert(warPile, opponentCard)

    -- 3. Calculate effective values for *these* cards
    local playerEffValue = calculateEffectiveValue(playerCard, opponentCard.class, playerItem)
    local opponentEffValue = calculateEffectiveValue(opponentCard, playerCard.class, opponentItem)

    -- 4. Compare and determine winner of the war
    local warWinner = nil
    if playerEffValue > opponentEffValue then
        warWinner = "player"
    elseif opponentEffValue > playerEffValue then
        warWinner = "opponent"
    else
        -- Tie during war resolution - Let's give it to the player for simplicity
        -- Or could discard pile, or recurse (but avoiding recursion for now)
        warWinner = "player"
         message = string.format("War Tiebreaker! %s (%d) vs %s (%d). Player wins tie! Press Space.",
                                getCardString(playerCard), playerEffValue,
                                getCardString(opponentCard), opponentEffValue)
    end

    if warWinner == "player" then
         message = string.format("Player wins the WAR! %s (%d) vs %s (%d). Takes %d cards. Press Space.",
                                getCardString(playerCard), playerEffValue,
                                getCardString(opponentCard), opponentEffValue, #warPile)
        for _, card in ipairs(warPile) do
            table.insert(playerDeck, card)
        end
        -- Award item on War win!
        local newItem = awardRandomItem()
        if newItem then
            playerItem = newItem
            message = message .. " Player found " .. playerItem.name .. "!"
        end

    elseif warWinner == "opponent" then
         message = string.format("Opponent wins the WAR! %s (%d) vs %s (%d). Takes %d cards. Press Space.",
                                getCardString(playerCard), playerEffValue,
                                getCardString(opponentCard), opponentEffValue, #warPile)
        for _, card in ipairs(warPile) do
            table.insert(opponentDeck, card)
        end
        -- Award item on War win!
        local newItem = awardRandomItem()
         if newItem then
            opponentItem = newItem
            message = message .. " Opponent found " .. opponentItem.name .. "!"
        end
    end

    warPile = {} -- Clear the pile
    playerCard = nil -- Clear revealed cards
    opponentCard = nil
    GAME_STATE = "playing" -- Return to normal play state

end

-- ========================================
-- Input Handling
-- ========================================

function love.keypressed(key)
    if key == "space" then
        if GAME_STATE == "menu" then
            startGame()
        elseif GAME_STATE == "playing" then
             -- Only allow playing a round if cards aren't currently shown
            if playerCard == nil and opponentCard == nil then
                 playRound()
            end
        elseif GAME_STATE == "war" then
            resolveWar()
        end
    elseif key == "r" then
        if GAME_STATE == "gameover" or GAME_STATE == "playing" or GAME_STATE == "war" then -- Allow restart anytime after starting
             startGame() -- Restart the game
        end
    elseif key == "escape" then
        love.event.quit()
    end
end
