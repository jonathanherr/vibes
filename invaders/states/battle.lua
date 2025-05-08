-- states/battle.lua
local BattleState = {}

-- Entity tables
local invaders = {}
local defender = nil
local invaderShots = {}
local defenderShots = {}
local shields = {}

-- Battle parameters (modified by powerups)
local invaderSpeed = 75 -- pixels per second horizontal (was 50)
local invaderMoveDownAmount = 20
local invaderHorizontalDir = 1 -- 1 for right, -1 for left
local invaderMoveTimer = 0.4 -- seconds until next horizontal move (was 0.5)
local invaderMoveTimerMax = 0.4 -- (was 0.5)
local invaderFireTimerMax = 1.2 -- seconds between invader shots (was 2)
local invaderFireTimer = invaderFireTimerMax
local invaderBaseHealth = 1
local invaderShieldDamageMultiplier = 1

local defenderSpeed = 220 -- pixels per second (was 150)
local defenderFireTimerMax = 0.6 -- seconds between defender shots (was 1)
local defenderFireTimer = 0

local shieldBlockHealth = 2

-- Battle dimensions (adjust based on window size)
local battleArea = {x = 50 * GameScale, y = 80 * GameScale, width = 540 * GameScale, height = 300 * GameScale}
local defenderY = love.graphics.getHeight() - 50 * GameScale

-- Temp variables for battle setup
local initialInvaderTypes = {} -- Types of invaders based on selected ship cards

function BattleState.enter(params)
    print("Entering Battle State")
    invaders = {}
    invaderShots = {}
    defenderShots = {}
    shields = {}
    initialInvaderTypes = {}

    -- Reset battle parameters to defaults before applying powerups
    invaderSpeed = 75
    invaderMoveTimerMax = 0.4
    invaderFireTimerMax = 1.2
    invaderBaseHealth = 1
    invaderShieldDamageMultiplier = 1
    defenderSpeed = 220
    defenderFireTimerMax = 0.6
    shieldBlockHealth = 2
    local defenderHealth = 10 -- Default defender health, initialized before card effects

    -- Process selected cards
    if params and params.selectedCards then
        for _, card in ipairs(params.selectedCards) do
            if card.type == "ship" then
                 for i = 1, 5 do -- Assume 5 invaders per row for now
                     table.insert(initialInvaderTypes, card.effect.type)
                 end

            elseif card.type == "powerup" then
                if card.effect.modifier == "invaderSpeed" then invaderSpeed = invaderSpeed * card.effect.value end
                if card.effect.modifier == "invaderFireRate" then invaderFireTimerMax = invaderFireTimerMax * card.effect.value end
                if card.effect.modifier == "invaderHealth" then invaderBaseHealth = invaderBaseHealth * card.effect.value end
                if card.effect.modifier == "invaderShieldDamage" then invaderShieldDamageMultiplier = invaderShieldDamageMultiplier * card.effect.value end
                if card.effect.modifier == "defenderFireRate" then defenderFireTimerMax = defenderFireTimerMax * card.effect.value end
                if card.effect.modifier == "defenderHealth" then defenderHealth = defenderHealth * card.effect.value end -- Now operates on the initialized local defenderHealth
                if card.effect.modifier == "defenderSpeed" then defenderSpeed = defenderSpeed * card.effect.value end
            end
        end
    end

    if #initialInvaderTypes == 0 then
         for i = 1, 10 do table.insert(initialInvaderTypes, "basic") end
    end

    local invaderSize = 30 * GameScale
    local invaderPadding = 10 * GameScale
    local invadersPerRow = 10

    local startX = battleArea.x + invaderPadding
    local startY = battleArea.y + invaderPadding

    local currentX = startX
    local currentY = startY
    local rowCount = 0
    local colCount = 0

     invaders = {}
     if params and params.selectedCards then
         local invaderCards = {}
         for _, card in ipairs(params.selectedCards) do
             if card.type == "ship" then
                 table.insert(invaderCards, card)
             end
         end

         if #invaderCards == 0 then
              table.insert(invaderCards, { effect = { type = "basic" }})
         end

         local invaderRowCount = #invaderCards
         local maxInvadersPerRow = math.floor(battleArea.width / (invaderSize + invaderPadding))
         invadersPerRow = math.min(10, maxInvadersPerRow)

         for rowIndex, card in ipairs(invaderCards) do
             local type = card.effect.type
             local baseHealth = invaderBaseHealth
             local speedModifier = 1

             local invaderRowStartX = battleArea.x + (battleArea.width - (invadersPerRow * (invaderSize + invaderPadding) - invaderPadding)) / 2
             local invaderRowY = battleArea.y + (rowIndex - 1) * (invaderSize + invaderPadding)

             for colIndex = 1, invadersPerRow do
                 local invaderX = invaderRowStartX + (colIndex - 1) * (invaderSize + invaderPadding)
                 table.insert(invaders, {
                     x = invaderX,
                     y = invaderRowY,
                     width = invaderSize,
                     height = invaderSize,
                     type = type,
                     health = baseHealth,
                     maxHealth = baseHealth,
                     img = Assets.invaderImg,
                     speedMultiplier = 1,
                 })
             end
         end
     end

     for _, invader in ipairs(invaders) do
         if invader.type == "basic" then
             invader.img = Assets.invaderImg
         elseif invader.type == "fast" then
             invader.img = Assets.fastInvaderImg
             invader.speedMultiplier = 1.5
             invader.health = invader.health * 0.8
             invader.maxHealth = invader.health
         elseif invader.type == "tank" then
             invader.img = Assets.tankInvaderImg
             invader.speedMultiplier = 0.7
             invader.health = invader.health * 2
             invader.maxHealth = invader.health
         end
     end

    defender = {
        x = love.graphics.getWidth() / 2,
        y = defenderY,
        width = 40 * GameScale,
        height = 30 * GameScale,
        speed = defenderSpeed,
        health = defenderHealth, -- Uses the initialized local variable
        maxHealth = defenderHealth, -- Uses the initialized local variable
        img = Assets.defenderImg,
        fireTimer = 0,
        fireTimerMax = defenderFireTimerMax,
        moveTimer = 0,
        moveInterval = 2,
        moveDir = 1,
    }

    local shieldCount = 4
    local shieldWidth = 60 * GameScale
    local shieldHeight = 40 * GameScale
    local shieldPadding = 50 * GameScale
    local shieldY = defenderY - shieldHeight - 30 * GameScale
    local totalShieldsWidth = shieldCount * shieldWidth + (shieldCount - 1) * shieldPadding
    local shieldStartX = (love.graphics.getWidth() - totalShieldsWidth) / 2

    for i = 1, shieldCount do
        table.insert(shields, {
            x = shieldStartX + (i - 1) * (shieldWidth + shieldPadding),
            y = shieldY,
            width = shieldWidth,
            height = shieldHeight,
            health = shieldBlockHealth,
            maxHealth = shieldBlockHealth,
            img = Assets.shieldBlockImg,
        })
    end

    invaderMoveTimer = invaderMoveTimerMax
    invaderFireTimer = invaderFireTimerMax
    defender.fireTimer = defender.fireTimerMax
end

function BattleState.update(dt)
    if #invaders == 0 then
        changeState("gameOver", { win = true })
        return
    end

    if defender.health <= 0 then
         changeState("gameOver", { win = true })
         return
    end

    for i = #invaders, 1, -1 do
        if invaders[i].y + invaders[i].height > defender.y then
            changeState("gameOver", { win = false })
            return
        end
    end

    invaderMoveTimer = invaderMoveTimer - dt
    if invaderMoveTimer <= 0 then
        local moveAmountX = invaderSpeed * invaderMoveTimerMax * GameScale
        local dropAmount = 0
        local hitEdge = false

        local leftMost = math.huge
        local rightMost = 0
        for _, invader in ipairs(invaders) do
            leftMost = math.min(leftMost, invader.x)
            rightMost = math.max(rightMost, invader.x + invader.width)
        end

        if invaderHorizontalDir == 1 and rightMost + moveAmountX > battleArea.x + battleArea.width then
            hitEdge = true
            invaderHorizontalDir = -1
            dropAmount = invaderMoveDownAmount * GameScale
        elseif invaderHorizontalDir == -1 and leftMost - moveAmountX < battleArea.x then
            hitEdge = true
            invaderHorizontalDir = 1
            dropAmount = invaderMoveDownAmount * GameScale
        end

        for _, invader in ipairs(invaders) do
            if not hitEdge then
                 invader.x = invader.x + (invaderSpeed * invader.speedMultiplier) * invaderMoveTimerMax * invaderHorizontalDir * GameScale
            else
                 invader.y = invader.y + dropAmount
            end
        end

        invaderMoveTimer = invaderMoveTimerMax
        invaderMoveTimerMax = invaderMoveTimerMax * 0.97 -- Speeds up more quickly (was 0.98)
        if Assets.invaderMoveSound and 
           type(Assets.invaderMoveSound.isFinished) == "function" and 
           Assets.invaderMoveSound:isFinished() and 
           type(Assets.invaderMoveSound.play) == "function" then
            Assets.invaderMoveSound:play()
        end
    end

    invaderFireTimer = invaderFireTimer - dt
    if invaderFireTimer <= 0 and #invaders > 0 then
        local firingInvaders = {}
        local columns = {}
        for _, invader in ipairs(invaders) do
            local colX = math.floor(invader.x / 10) * 10
            if not columns[colX] or invader.y > columns[colX].y then
                columns[colX] = invader
            end
        end
        for _, invader in pairs(columns) do
             table.insert(firingInvaders, invader)
        end

        if #firingInvaders > 0 then
            local shooter = nil
            if #firingInvaders == 1 then
                shooter = firingInvaders[1]
            else
                -- Smarter targeting: pick invader column closest to defender
                local closestDist = math.huge
                for _, inv in ipairs(firingInvaders) do
                    local dist = math.abs(inv.x - defender.x)
                    if dist < closestDist then
                        closestDist = dist
                        shooter = inv
                    elseif dist == closestDist and math.random(2) == 1 then -- Random tie-break
                        shooter = inv
                    end
                end
                if not shooter then shooter = firingInvaders[math.random(#firingInvaders)] end -- Fallback if all are equidistant or issue
            end

            if shooter then
                 table.insert(invaderShots, {
                     x = shooter.x + shooter.width / 2,
                     y = shooter.y + shooter.height,
                     radius = 3 * GameScale,
                     speed = 150 * GameScale,
                     owner = "invader",
                 })
                if Assets.shootSound then Assets.shootSound:play() end
            end
        end

        invaderFireTimer = invaderFireTimerMax
    end

    defender.moveTimer = defender.moveTimer - dt
    if defender.moveTimer <= 0 then
        -- Smarter auto-movement: tend towards center of battle area
        local targetX = battleArea.x + battleArea.width / 2
        if defender.x < targetX - defender.width * 1.5 then -- Give some buffer
            defender.moveDir = 1
        elseif defender.x > targetX + defender.width * 0.5 then -- Give some buffer
            defender.moveDir = -1
        else
            defender.moveDir = ({ -1, 0, 1 })[math.random(3)] -- Random if near center
        end
        defender.moveInterval = math.random(1, 2) -- Shorter interval for more responsiveness
        defender.moveTimer = defender.moveInterval
    end
    defender.x = defender.x + defender.moveDir * defender.speed * dt * GameScale
    defender.x = math.max(battleArea.x, defender.x)
    defender.x = math.min(battleArea.x + battleArea.width - defender.width, defender.x)

    defender.fireTimer = defender.fireTimer - dt
    if defender.fireTimer <= 0 then
         table.insert(defenderShots, {
             x = defender.x + defender.width / 2,
             y = defender.y,
             radius = 3 * GameScale,
             speed = 300 * GameScale,
             owner = "defender",
         })
        if Assets.shootSound then Assets.shootSound:play() end
        defender.fireTimer = defender.fireTimerMax
    end

    for i = #invaderShots, 1, -1 do
        invaderShots[i].y = invaderShots[i].y + invaderShots[i].speed * dt
        if invaderShots[i].y > love.graphics.getHeight() then
            table.remove(invaderShots, i)
        end
    end
    for i = #defenderShots, 1, -1 do
        defenderShots[i].y = defenderShots[i].y - defenderShots[i].speed * dt
         if defenderShots[i].y < 0 then
            table.remove(defenderShots, i)
        end
    end

    for i = #defenderShots, 1, -1 do
        local shot = defenderShots[i]
        local shotHit = false
        for j = #invaders, 1, -1 do
            local invader = invaders[j]
            if shot.x < invader.x + invader.width and
               shot.x + shot.radius*2 > invader.x and
               shot.y < invader.y + invader.height and
               shot.y + shot.radius*2 > invader.y then
                invader.health = invader.health - 1
                if invader.health <= 0 then
                    table.remove(invaders, j)
                    if Assets.explosionSound then Assets.explosionSound:play() end
                end
                shotHit = true
                break
            end
        end
        if shotHit then
            table.remove(defenderShots, i)
        end
    end

     for i = #defenderShots, 1, -1 do
        local shot = defenderShots[i]
        local shotHit = false
        for j = #shields, 1, -1 do
            local shield = shields[j]
            if shield.health > 0 and
               shot.x < shield.x + shield.width and
               shot.x + shot.radius*2 > shield.x and
               shot.y < shield.y + shield.height and
               shot.y + shot.radius*2 > shield.y then
                shield.health = shield.health - 1
                shotHit = true
                break
            end
        end
        if shotHit then
            table.remove(defenderShots, i)
        end
    end

    for i = #invaderShots, 1, -1 do
        local shot = invaderShots[i]
        if shot.x < defender.x + defender.width and
           shot.x + shot.radius*2 > defender.x and
           shot.y < defender.y + defender.height and
           shot.y + shot.radius*2 > defender.y then
             defender.health = defender.health - 1
             table.remove(invaderShots, i)
             if Assets.explosionSound then Assets.explosionSound:play() end
             break
        end
    end

     for i = #invaderShots, 1, -1 do
        local shot = invaderShots[i]
        local shotHit = false
        for j = #shields, 1, -1 do
            local shield = shields[j]
             if shield.health > 0 and
               shot.x < shield.x + shield.width and
               shot.x + shot.radius*2 > shield.x and
               shot.y < shield.y + shield.height and
               shot.y + shot.radius*2 > shield.y then
                shield.health = shield.health - (1 * invaderShieldDamageMultiplier)
                 if shield.health < 0 then shield.health = 0 end
                shotHit = true
                break
            end
        end
        if shotHit then
            table.remove(invaderShots, i)
        end
    end

     for i = #shields, 1, -1 do
         if shields[i].health <= 0 then
         end
     end
end

function BattleState.draw()
    love.graphics.setColor(1, 1, 1)

    love.graphics.setColor(0.2, 0.2, 0.2, 0.5)
    love.graphics.rectangle("line", battleArea.x, battleArea.y, battleArea.width, battleArea.height)
    love.graphics.setColor(1, 1, 1)

    for _, invader in ipairs(invaders) do
         local hpBarWidth = invader.width
         local hpBarHeight = 3 * GameScale
         local currentHpWidth = (invader.health / invader.maxHealth) * hpBarWidth
         love.graphics.setColor(1, 0, 0, 0.7)
         love.graphics.rectangle("fill", invader.x, invader.y - hpBarHeight - 2 * GameScale, hpBarWidth, hpBarHeight)
         love.graphics.setColor(0, 1, 0, 0.7)
         love.graphics.rectangle("fill", invader.x, invader.y - hpBarHeight - 2 * GameScale, currentHpWidth, hpBarHeight)
         love.graphics.setColor(1, 1, 1)

        love.graphics.draw(invader.img, invader.x, invader.y, 0, invader.width / invader.img:getWidth(), invader.height / invader.img:getHeight())
    end

     if defender.health > 0 then
         local hpBarWidth = defender.width
         local hpBarHeight = 5 * GameScale
         local currentHpWidth = (defender.health / defender.maxHealth) * hpBarWidth
         love.graphics.setColor(1, 0, 0, 0.7)
         love.graphics.rectangle("fill", defender.x, defender.y - hpBarHeight - 5 * GameScale, hpBarWidth, hpBarHeight)
         love.graphics.setColor(0, 1, 0, 0.7)
         love.graphics.rectangle("fill", defender.x, defender.y - hpBarHeight - 5 * GameScale, currentHpWidth, hpBarHeight)
         love.graphics.setColor(1, 1, 1)

         love.graphics.draw(defender.img, defender.x, defender.y, 0, defender.width / defender.img:getWidth(), defender.height / defender.img:getHeight())
     end

    love.graphics.setColor(1, 0, 0)
    for _, shot in ipairs(invaderShots) do
        love.graphics.circle("fill", shot.x, shot.y, shot.radius)
    end
    love.graphics.setColor(0, 1, 0)
    for _, shot in ipairs(defenderShots) do
        love.graphics.circle("fill", shot.x, shot.y, shot.radius)
    end
    love.graphics.setColor(1, 1, 1)

    for _, shield in ipairs(shields) do
         if shield.health > 0 then
              love.graphics.setColor(0, 0, 1, shield.health / shield.maxHealth * 0.8 + 0.2)
              love.graphics.rectangle("fill", shield.x, shield.y, shield.width, shield.height)
              love.graphics.setColor(1, 1, 1)
         end
    end

     love.graphics.setColor(1, 1, 1)
     love.graphics.print("Defender HP: " .. math.ceil(defender.health), 10 * GameScale, love.graphics.getHeight() - 30 * GameScale)
end

function BattleState.exit()
    print("Exiting Battle State")
    invaders = {}
    defender = nil
    invaderShots = {}
    defenderShots = {}
    shields = {}
end

return BattleState
