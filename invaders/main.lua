-- main.lua
local currentState
local states = {}
local selectedCards = {} -- Stores cards chosen in the selection phase

-- Global Assets table - will be populated below
Assets = {}

-- Design resolution
DESIGN_WIDTH = 800
DESIGN_HEIGHT = 600
GameScale = 1 -- Default, will be updated in love.load

function love.load()
    -- Set window properties (optional but good for retro feel)
    love.window.setMode(1280, 960, {fullscreen = false, resizable = true, borderless = false, vsync = true})
    love.window.setTitle("Invader Manager")

    -- Calculate scale factor
    local currentWidth, currentHeight = love.graphics.getDimensions()
    local scaleX = currentWidth / DESIGN_WIDTH
    local scaleY = currentHeight / DESIGN_HEIGHT
    GameScale = math.min(scaleX, scaleY) -- Use the smaller scale to fit all content, or choose one like scaleX

    -- Load assets (fonts, images, sounds) - POPULATE ASSETS *BEFORE* REQUIRING STATES
    -- Assets table was defined globally above
    Assets.font = love.graphics.newFont("EightBit.ttf", 24) -- Need a pixel font!
    -- Placeholder assets - replace with actual images/sounds
    -- Make sure these image files exist!
    Assets.invaderImg = love.graphics.newImage("invader.png") -- Basic invader
    Assets.fastInvaderImg = love.graphics.newImage("fast_invader.png")
    Assets.tankInvaderImg = love.graphics.newImage("tank_invader.png")
    Assets.defenderImg = love.graphics.newImage("defender.png")
    Assets.shieldBlockImg = love.graphics.newImage("shield_block.png")
    Assets.invaderShotImg = love.graphics.newImage("invader_shot.png")
    Assets.defenderShotImg = love.graphics.newImage("defender_shot.png")
    Assets.cardBackImg = love.graphics.newImage("card_back.png")

    -- Make sure these sound files exist!
    Assets.shootSound = love.audio.newSource("shoot.wav", "static")
    Assets.explosionSound = love.audio.newSource("explosion.wav", "static")
    Assets.invaderMoveSound = love.audio.newSource("invadermove.wav", "static")

    -- Set default font - now that Assets.font is loaded
    love.graphics.setFont(Assets.font)

    -- Require state files *AFTER* Assets are loaded and fonts set
    states.cardSelection = require("states.cardselection")
    states.battle = require("states.battle")
    states.gameOver = require("states.gameOver")

    -- Initialize and enter the first state
    -- states.cardSelection.init() -- Removed init call here, init should happen implicitly in enter
    -- states.battle.init() -- Removed init call here
    -- states.gameOver.init() -- Removed init call here
    -- Init calls are usually not needed if enter/exit handle setup/cleanup
    -- If you *do* have init functions, call them after requiring:
     for k, v in pairs(states) do
         if v.init then v.init() end
     end


    changeState("cardSelection")
end

function love.update(dt)
    if currentState and currentState.update then
        currentState.update(dt)
    end
end

function love.draw()
    -- Draw a black background
    love.graphics.setColor(0, 0, 0)
    love.graphics.rectangle("fill", 0, 0, love.graphics.getWidth(), love.graphics.getHeight())

    -- Draw current state
    if currentState and currentState.draw then
        currentState.draw()
    end

    -- Draw FPS (optional) - Now safe to access Assets.font
    love.graphics.setColor(1, 1, 1, 0.5)
    love.graphics.setFont(Assets.font) -- Ensure font is set
    love.graphics.print("FPS: "..tostring(love.timer.getFPS(60)), 10 * GameScale, 10 * GameScale, 0, GameScale, GameScale) -- Scaled position and text size
    love.graphics.setColor(1, 1, 1) -- Reset color
end

function love.keypressed(key)
    if currentState and currentState.keypressed then
        currentState.keypressed(key)
    end
end

function love.mousepressed(x, y, button)
    if currentState and currentState.mousepressed then
        currentState.mousepressed(x, y, button)
    end
end

function love.mousereleased(x, y, button)
    if currentState and currentState.mousereleased then
        currentState.mousereleased(x, y, button)
    end
end

-- Function to change game state
function changeState(newStateName, params)
    if currentState and currentState.exit then
        currentState.exit()
    end

    currentState = states[newStateName]

    if currentState and currentState.enter then
        currentState.enter(params) -- Pass parameters like selected cards
    end
end