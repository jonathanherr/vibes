-- states/gameOver.lua
local GameOverState = {}

local win = false
-- Scaled playAgainButton dimensions and position
local playAgainButton = {x = 250 * GameScale, y = 350 * GameScale, width = 150 * GameScale, height = 50 * GameScale}

function GameOverState.enter(params)
    print("Entering Game Over State")
    win = params and params.win or false -- Default to false if no param
end

function GameOverState.update(dt)
    -- Nothing much to update here
end

function GameOverState.draw()
    love.graphics.setFont(Assets.font) -- Ensure font is set

    local message = win and "You Win!" or "Game Over!"
    local textWidth = Assets.font:getWidth(message) * GameScale * 2 -- Scale font for game over message
    local textHeight = Assets.font:getHeight() * GameScale * 2

    love.graphics.printf(message, (love.graphics.getWidth() - textWidth) / 2, (love.graphics.getHeight() - textHeight) / 2, textWidth, "center")

    love.graphics.setFont(Assets.font) -- Reset font for smaller text
    local restartMessage = "Press Enter to Restart"
    local restartWidth = Assets.font:getWidth(restartMessage) * GameScale
    local restartTextWidthLimit = love.graphics.getWidth() -- Or a specific scaled width
    love.graphics.printf(restartMessage, 0, (love.graphics.getHeight() / 2) + 50 * GameScale, love.graphics.getWidth(), "center")

    -- Draw Play Again button
    local buttonColor = {0, 0.5, 1} -- Blueish
    love.graphics.setColor(unpack(buttonColor))
    love.graphics.rectangle("fill", playAgainButton.x, playAgainButton.y, playAgainButton.width, playAgainButton.height)
    love.graphics.setColor(1, 1, 1)
    love.graphics.rectangle("line", playAgainButton.x, playAgainButton.y, playAgainButton.width, playAgainButton.height)
    -- Correctly center text within the scaled button height
    love.graphics.printf("Play Again", playAgainButton.x, playAgainButton.y + (playAgainButton.height - Assets.font:getHeight() * GameScale)/2, playAgainButton.width, "center")
end

function GameOverState.mousepressed(x, y, button)
    if button == 1 then -- Left click
        -- Check Play Again button click
        if x > playAgainButton.x and x < playAgainButton.x + playAgainButton.width and y > playAgainButton.y and y < playAgainButton.y + playAgainButton.height then
            -- Transition back to card selection state
            changeState("cardSelection")
        end
    end
end

function GameOverState.exit()
    print("Exiting Game Over State")
    -- Clean up
end

return GameOverState
