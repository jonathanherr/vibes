-- main.lua

-- LÖVE 2D requires initializing variables outside functions
-- if they need to be accessed across different callback functions.

-- Game Settings
local CANVAS_WIDTH = 800
local CANVAS_HEIGHT = 600
local LANE_WIDTH = CANVAS_WIDTH / 4
local BOAT_WIDTH = 40
local BOAT_HEIGHT = 70
local FINISH_LINE_Y = 50
local BOAT_ACCELERATION = 150 -- Pixels per second^2
local BOAT_DECELERATION = 80  -- Pixels per second^2
local MAX_SPEED = 250         -- Pixels per second
local WATER_RIPPLE_SPEED = 20 -- Rate of change for offset
local FAN_ANIMATION_SPEED = 5 -- Radians per second

-- Game State
local gameState = 'waiting' -- 'waiting', 'countdown', 'running', 'finished'
local winner = nil
local countdown = 3
local countdownTimer = 0 -- Use a timer based on dt
local keysPressed = {} -- Keep track of keys currently held down
local waterOffset = 0
local fanBounce = 0 -- For simple fan animation

-- Boat Objects (Tables in Lua)
local boat1 = {
    x = LANE_WIDTH - BOAT_WIDTH / 2,
    y = CANVAS_HEIGHT - BOAT_HEIGHT - 20,
    width = BOAT_WIDTH,
    height = BOAT_HEIGHT,
    color = { 229/255, 57/255, 53/255, 1 }, -- Red (r,g,b,a 0-1 range)
    speed = 0,
    control = 'w'
}

local boat2 = {
    x = CANVAS_WIDTH - LANE_WIDTH - BOAT_WIDTH / 2,
    y = CANVAS_HEIGHT - BOAT_HEIGHT - 20,
    width = BOAT_WIDTH,
    height = BOAT_HEIGHT,
    color = { 30/255, 136/255, 229/255, 1 }, -- Blue (r,g,b,a 0-1 range)
    speed = 0,
    control = 'up' -- LÖVE key name for Up Arrow
}

-- Font for UI text
local uiFontLarge = love.graphics.newFont(40)
local uiFontMedium = love.graphics.newFont(24)
local uiFontSmall = love.graphics.newFont(14)
local uiFontTiny = love.graphics.newFont(10)

-- Helper function to lighten/darken (adjusts brightness)
function lightenDarkenColor(color, amount)
    local r = math.max(0, math.min(1, color[1] + amount/255))
    local g = math.max(0, math.min(1, color[2] + amount/255))
    local b = math.max(0, math.min(1, color[3] + amount/255))
    return {r, g, b, color[4]}
end

-- Game Logic Functions
function startGameCountdown()
    gameState = 'countdown'
    countdown = 3
    countdownTimer = 1 -- Start a 1-second timer for the first number
end

function resetGame()
    winner = nil
    gameState = 'waiting'
    boat1.y = CANVAS_HEIGHT - BOAT_HEIGHT - 20
    boat1.speed = 0
    boat2.y = CANVAS_HEIGHT - BOAT_HEIGHT - 20
    boat2.speed = 0
    keysPressed = {}
    countdown = 3
    countdownTimer = 0
end

function endGame()
    gameState = 'finished'
    -- Winner message drawn in love.draw
end

-- LÖVE Callback Functions

function love.load()
    -- Set background color (acts like base water)
    love.graphics.setBackgroundColor(77/255, 208/255, 225/255) -- #4dd0e1
    resetGame() -- Initialize game state
    math.randomseed(os.time()) -- Seed random generator for cheering
end

function love.update(dt) -- dt is delta time (time since last frame)
    -- Update animations independent of game state
    waterOffset = (waterOffset + WATER_RIPPLE_SPEED * dt) % 20
    fanBounce = math.sin(love.timer.getTime() * FAN_ANIMATION_SPEED) * 3

    if gameState == 'countdown' then
        countdownTimer = countdownTimer - dt
        if countdownTimer <= 0 then
            countdown = countdown - 1
            if countdown > 0 then
                countdownTimer = 1 -- Reset timer for next number
            elseif countdown == 0 then
                 countdownTimer = 1 -- Timer for "GO!" message duration
                 -- Don't change state yet, wait for GO! timer
            else -- countdown < 0 means GO! timer finished
                gameState = 'running'
            end
        end

    elseif gameState == 'running' then
        -- Update Boat 1
        if love.keyboard.isDown(boat1.control) then
            boat1.speed = boat1.speed + BOAT_ACCELERATION * dt
        else
            boat1.speed = boat1.speed - BOAT_DECELERATION * dt
        end
        boat1.speed = math.max(0, math.min(boat1.speed, MAX_SPEED)) -- Clamp speed
        boat1.y = boat1.y - boat1.speed * dt

        -- Update Boat 2
        if love.keyboard.isDown(boat2.control) then
            boat2.speed = boat2.speed + BOAT_ACCELERATION * dt
        else
            boat2.speed = boat2.speed - BOAT_DECELERATION * dt
        end
        boat2.speed = math.max(0, math.min(boat2.speed, MAX_SPEED)) -- Clamp speed
        boat2.y = boat2.y - boat2.speed * dt

        -- Check for Winner
        local boat1Finished = boat1.y <= FINISH_LINE_Y
        local boat2Finished = boat2.y <= FINISH_LINE_Y

        if boat1Finished and boat2Finished then
            if boat1.y < boat2.y then winner = 'Player 1 (Red)'
            elseif boat2.y < boat1.y then winner = 'Player 2 (Blue)'
            else winner = "It's a Tie!" end
            endGame()
        elseif boat1Finished then
            winner = 'Player 1 (Red)'
            endGame()
        elseif boat2Finished then
            winner = 'Player 2 (Blue)'
            endGame()
        end
    end
end

function love.keypressed(key)
    if key == 'return' then -- 'return' is the Enter key in LÖVE
        if gameState == 'waiting' then
            startGameCountdown()
        elseif gameState == 'finished' then
            resetGame()
        end
    end

    -- Track pressed keys (might be useful for other things, though isDown is used for movement)
    keysPressed[key] = true
end

function love.keyreleased(key)
    keysPressed[key] = false
end


-- Drawing Functions --

function drawWater()
    -- Background is set in love.load
    -- Simple ripple effect
    love.graphics.setLineWidth(2)
    love.graphics.setColor(1, 1, 1, 0.3) -- White ripples
    for y = 0, CANVAS_HEIGHT, 20 do
        local points = {}
        for x = 0, CANVAS_WIDTH, 10 do
            table.insert(points, x)
            table.insert(points, y + math.sin(x * 0.05 + y * 0.1 + waterOffset) * 3)
        end
        if #points >= 4 then -- Need at least 2 points (4 coordinates) to draw a line
             love.graphics.line(points)
        end
    end
     love.graphics.setLineWidth(1) -- Reset line width
end

function drawLanes()
    -- Center lane divider
    love.graphics.setLineWidth(5)
    love.graphics.setColor(1, 1, 1, 0.5) -- White lane line
    love.graphics.line(CANVAS_WIDTH / 2, 0, CANVAS_WIDTH / 2, CANVAS_HEIGHT)
    love.graphics.setLineWidth(1)

    -- Finish Line (checkered flag style)
    local checkSize = 20
    local finishLineHeight = checkSize -- Make it thicker for visibility
    for x = 0, CANVAS_WIDTH - checkSize, checkSize do
        for yOffset = 0, finishLineHeight - checkSize / 2, checkSize / 2 do
             local effectiveY = FINISH_LINE_Y + yOffset
             if (math.floor(x / checkSize) + math.floor(yOffset / (checkSize/2))) % 2 == 0 then
                 love.graphics.setColor(1, 1, 1, 1) -- White
             else
                 love.graphics.setColor(0, 0, 0, 1) -- Black
             end
             love.graphics.rectangle('fill', x, effectiveY, checkSize, checkSize / 2)
        end
    end

     -- Finish text
     love.graphics.setColor(1, 1, 0, 1) -- Yellow
     love.graphics.setFont(uiFontSmall)
     love.graphics.printf('FINISH', 0, FINISH_LINE_Y - 15, CANVAS_WIDTH, 'center')
end

function drawBoat(boat)
    -- Boat Body
    love.graphics.setColor(boat.color)
    love.graphics.rectangle('fill', boat.x, boat.y, boat.width, boat.height)

    -- Simple Cabin/Top
    local darkerColor = lightenDarkenColor(boat.color, -60)
    love.graphics.setColor(darkerColor)
    love.graphics.rectangle('fill', boat.x + boat.width * 0.1, boat.y + boat.height * 0.1, boat.width * 0.8, boat.height * 0.3)

    -- Boat "Fan" (simple circle at the back)
    love.graphics.setColor(170/255, 170/255, 170/255, 1) -- Grey fan #aaaaaa
    love.graphics.circle('fill', boat.x + boat.width / 2, boat.y + boat.height + 5, boat.width / 3)

    -- Spray effect (simple particles) when moving fast
    if boat.speed > MAX_SPEED * 0.5 then
        love.graphics.setColor(1, 1, 1, 0.7)
        for i = 1, 5 do
            local sprayX = boat.x + math.random() * boat.width
            local sprayY = boat.y + boat.height + math.random() * 15 -- Below the boat
            local spraySize = math.random() * 3 + 1
            love.graphics.rectangle('fill', sprayX, sprayY, spraySize, spraySize)
        end
    end
end

function drawCheerBubble(x, y, text)
    local bubbleWidth = 35
    local bubbleHeight = 15
    local textYOffset = -10 - bubbleHeight / 2 + 2 -- Adjust based on font

    -- Background
    love.graphics.setColor(1, 1, 1, 0.8)
    love.graphics.rectangle('fill', x - bubbleWidth / 2, y - bubbleHeight - 10, bubbleWidth, bubbleHeight, 3, 3) -- Rounded slightly

    -- Outline
    love.graphics.setColor(0, 0, 0, 1)
    love.graphics.setLineWidth(1)
    love.graphics.rectangle('line', x - bubbleWidth / 2, y - bubbleHeight - 10, bubbleWidth, bubbleHeight, 3, 3)

    -- Text inside
    love.graphics.setFont(uiFontTiny)
    love.graphics.printf(text, x - bubbleWidth / 2, y + textYOffset, bubbleWidth, 'center')
end


function drawFans()
    local fanZoneWidth = LANE_WIDTH - BOAT_WIDTH / 2 - 10
    local fanSize = 10
    local fanSpacing = fanSize * 1.5
    local numFans = math.floor(fanZoneWidth / fanSpacing)
    local fanYStart = FINISH_LINE_Y + 30
    local fanYEnd = CANVAS_HEIGHT - 30

    local cheerTexts = {'GO!', 'YEAH!', 'FAST!', '<3', 'WIN!'}


    for y = fanYStart, fanYEnd, fanSize * 3 do -- Rows of fans
         local currentBounce = fanBounce * ( (math.floor(y / (fanSize * 3)) % 2) * 2 - 1) -- Alternate bounce direction per row

        -- Left side fans
        for i = 0, numFans - 1 do
            local fanX = 10 + i * fanSpacing + fanSize / 2
             -- Orange/Peach colors #ffab91, #ffcc80
            if i % 2 == 0 then love.graphics.setColor(255/255, 171/255, 145/255, 1)
            else love.graphics.setColor(255/255, 204/255, 128/255, 1) end
            love.graphics.circle('fill', fanX, y + currentBounce, fanSize / 2)

             -- Random cheering bubble
            if gameState == 'running' and math.random() < 0.0005 then -- Lower chance per frame
                 drawCheerBubble(fanX, y + currentBounce, cheerTexts[math.random(#cheerTexts)])
            end
        end

        -- Right side fans
        for i = 0, numFans - 1 do
            local fanX = CANVAS_WIDTH - fanZoneWidth + i * fanSpacing + fanSize/2;
            -- Teal/Green colors #80cbc4, #a5d6a7
            if i % 2 == 0 then love.graphics.setColor(128/255, 203/255, 196/255, 1)
            else love.graphics.setColor(165/255, 214/255, 167/255, 1) end
            love.graphics.circle('fill', fanX, y + currentBounce, fanSize / 2)

            -- Random cheering bubble
            if gameState == 'running' and math.random() < 0.0005 then -- Lower chance per frame
                  drawCheerBubble(fanX, y + currentBounce, cheerTexts[math.random(#cheerTexts)])
            end
        end
    end
end


function drawUI()
    love.graphics.setColor(1, 1, 1, 1) -- White text

    if gameState == 'waiting' then
        love.graphics.setFont(uiFontLarge)
        love.graphics.printf("Press Enter to Start", 0, CANVAS_HEIGHT / 2 - 60, CANVAS_WIDTH, 'center')
        love.graphics.setFont(uiFontMedium)
        love.graphics.printf("Player 1 (Red): W Key", 0, CANVAS_HEIGHT / 2 + 0, CANVAS_WIDTH, 'center')
        love.graphics.printf("Player 2 (Blue): Up Arrow", 0, CANVAS_HEIGHT / 2 + 30, CANVAS_WIDTH, 'center')

    elseif gameState == 'countdown' then
        love.graphics.setFont(uiFontLarge)
        local text = ""
        if countdown > 0 then text = tostring(countdown)
        elseif countdown == 0 then text = "GO!"
        end
         -- Draw background box for visibility
         local textWidth = uiFontLarge:getWidth(text)
         local textHeight = uiFontLarge:getHeight()
         love.graphics.setColor(0,0,0,0.5)
         love.graphics.rectangle('fill', CANVAS_WIDTH/2 - textWidth/2 - 10, CANVAS_HEIGHT/2 - textHeight/2 - 10, textWidth + 20, textHeight + 20, 5, 5)
         love.graphics.setColor(1,1,1,1)
         love.graphics.printf(text, 0, CANVAS_HEIGHT / 2 - textHeight / 2, CANVAS_WIDTH, 'center')


    elseif gameState == 'finished' then
         love.graphics.setFont(uiFontLarge)
         local winText = winner .. " Wins!"
         local textWidth = uiFontLarge:getWidth(winText)
         local textHeight = uiFontLarge:getHeight()

         -- Background box
         love.graphics.setColor(0,0,0,0.7)
         love.graphics.rectangle('fill', CANVAS_WIDTH/2 - textWidth/2 - 20, CANVAS_HEIGHT/2 - textHeight/2 - 30, textWidth + 40, textHeight + 70, 10, 10)

         -- Winner Text
         love.graphics.setColor(1,1,1,1)
         love.graphics.printf(winText, 0, CANVAS_HEIGHT / 2 - textHeight/2, CANVAS_WIDTH, 'center')

         -- Reset Text
         love.graphics.setFont(uiFontMedium)
         love.graphics.printf("Press Enter to Play Again", 0, CANVAS_HEIGHT / 2 + textHeight/2 + 10, CANVAS_WIDTH, 'center')
    end
end

function love.draw()
    -- Draw elements (order matters for layering)
    drawWater()
    drawLanes()
    drawFans()
    drawBoat(boat1)
    drawBoat(boat2)

    -- Draw UI overlay last
    drawUI()
end