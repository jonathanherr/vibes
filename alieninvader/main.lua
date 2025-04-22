--[[
Alien Invaders - Love2D Game
main.lua - Entry point and core game logic
]]

-- Global Variables (Consider moving to a dedicated 'player' or 'game' module later)
local gameState = "map" -- Current game state: "map", "combat", "harvesting", "traveling"
local playerResources = {
    quantonium = 0,
    zyther_crystals = 0,
    plasma_gel = 0,
    -- Add more resources as needed
}
local playerStats = {
    ship = {
        health = 100,
        maxHealth = 100,
        speed = 500, -- Increased speed
        damage = 10,
        fireRate = 0.2, -- Reduced fire rate for faster shooting
        shield = 60, -- current shield
        maxShield = 60, -- max shield
        shieldRegen = 10 -- shield points per second
    },
    armadaSize = 3 -- Lowered initial armada size
}

local planets = {}
local currentTargetPlanet = nil -- Stores the planet object selected for attack

local combatObjects = { -- Store all active objects in the combat state
    player = nil,
    playerArmada = {},
    enemies = {},
    bullets = {}
}

-- Track player score and scoreboard
local playerScore = 0
local scoreboard = {}
local showScoreboard = false

-- Scaling factors
local scaleX, scaleY = 1, 1
local BASE_WIDTH, BASE_HEIGHT = 1024, 768

local uiFonts = {
    normal = nil,
    large = nil
}

-- Galaxy progression variables
local galaxyLevel = 0
local newGalaxyMessage = nil
local newGalaxyTimer = 0
local NEW_GALAXY_MSG_TIME = 2.5

local isGameOver = false
local gameOverTimer = 0
local GAME_OVER_MSG_TIME = 3

-- Radio exclamations for ship destruction
local radioExclamations = {
    "I'm hit! Going down!",
    "Tell my family...",
    "Mayday! Mayday!",
    "Nooo!",
    "Ejecting! Ejecting!",
    "It's over for me!",
    "Arrgh!",
    "Goodbye, cruel galaxy...",
    "Systems failing!",
    "This can't be happening!"
}

-- Radio message state
local radioMessage = nil
local radioMessageTimer = 0
local RADIO_MSG_DURATION = 2.5

-- Galaxy background data (star clusters, scattered stars, constellations, clouds, etc.)
local galaxyBackground = nil

-- List of real-sounding galaxy names
local galaxyNames = {
    "Andromeda", "Centaurus A", "Sombrero", "Whirlpool", "Pinwheel", "Triangulum", "Cartwheel", "Black Eye", "Tadpole", "Sunflower", "Cigar", "Sculptor", "Messier 81", "Messier 82", "NGC 1300", "NGC 6744", "NGC 253", "NGC 300", "NGC 2403", "NGC 4414"
}

-- Utility to generate a random color from a palette
local function randomStarColor()
    local starColors = {
        {1,1,1,1}, {1,0.95,0.8,1}, {0.8,0.9,1,1}, {1,0.8,0.8,1}, {0.8,1,0.9,1}, {1,0.9,0.7,1}, {0.7,0.8,1,1}, {1,0.8,0.5,1}
    }
    return starColors[math.random(1,#starColors)]
end

local function generateGalaxyBackground()
    local bg = {}
    -- Randomly decide which features to include
    bg.includeClusters = math.random() < 0.8
    bg.includeScattered = math.random() < 0.8
    bg.includeConstellations = false -- Disable constellations
    bg.includeClouds = math.random() < 0.5

    -- Star clusters
    bg.clusters = {}
    if bg.includeClusters then
        local clusterCount = math.random(2,4)
        for i=1,clusterCount do
            local cx = math.random(120, BASE_WIDTH-120)
            local cy = math.random(100, BASE_HEIGHT-100)
            local r = math.random(50, 120)
            local n = math.random(8, 18) -- Slightly more stars per cluster
            local color = {math.random(7,10)/10, math.random(7,10)/10, 1, 0.18}
            local stars = {}
            for j=1,n do
                local angle = math.random() * 2 * math.pi
                local dist = math.sqrt(math.random()) * r
                local x = cx + math.cos(angle) * dist
                local y = cy + math.sin(angle) * dist
                local c = randomStarColor()
                local size = math.random(1,3)
                table.insert(stars, {x=x, y=y, color=c, size=size})
            end
            table.insert(bg.clusters, {cx=cx, cy=cy, r=r, color=color, stars=stars})
        end
    end
    -- Scattered stars
    bg.scattered = {}
    if bg.includeScattered then
        for i=1,math.random(18,32) do -- More scattered stars
            local x = math.random(0, BASE_WIDTH)
            local y = math.random(0, BASE_HEIGHT)
            local c = randomStarColor()
            local size = math.random(1,2)
            table.insert(bg.scattered, {x=x, y=y, color=c, size=size})
        end
    end
    -- Constellations (lines between stars) -- DISABLED
    bg.constellations = {}
    -- Clouds/nebulae
    bg.clouds = {}
    if bg.includeClouds then
        local cloudCount = math.random(1,2)
        for i=1,cloudCount do
            local cx = math.random(120, BASE_WIDTH-120)
            local cy = math.random(100, BASE_HEIGHT-100)
            local r = math.random(60, 160)
            local color = {math.random(6,10)/10, math.random(6,10)/10, math.random(7,10)/10, 0.10+math.random()*0.08}
            table.insert(bg.clouds, {cx=cx, cy=cy, r=r, color=color})
        end
    end
    return bg
end

function triggerGameOver()
    isGameOver = true
    gameOverTimer = GAME_OVER_MSG_TIME
    gameState = "gameover"
    table.insert(scoreboard, 1, {date=os.date("%Y-%m-%d %H:%M"), score=playerScore})
    showScoreboard = true
end

function drawGameOver()
    love.graphics.setColor(0, 0, 0, 0.8)
    love.graphics.rectangle("fill", 0, 0, love.graphics.getWidth(), love.graphics.getHeight())
    love.graphics.setColor(1, 0, 0)
    love.graphics.setFont(uiFonts.large)
    love.graphics.printf("GAME OVER", 0, love.graphics.getHeight() / 2 - 60, love.graphics.getWidth(), "center")
    love.graphics.setFont(uiFonts.normal)
    love.graphics.setColor(1, 1, 1)
    -- Only show restart message if not on scoreboard
    if not showScoreboard then
        love.graphics.printf("Restarting in a moment...", 0, love.graphics.getHeight() / 2 + 10, love.graphics.getWidth(), "center")
    end
    -- Draw scoreboard
    love.graphics.setFont(love.graphics.newFont(44))
    love.graphics.setColor(1, 1, 0.3)
    love.graphics.printf("SCOREBOARD", 0, 80, love.graphics.getWidth(), "center")
    love.graphics.setFont(love.graphics.newFont(32))
    for i, entry in ipairs(scoreboard) do
        local entryText = string.format("%2d. %s  %d", i, entry.date, entry.score)
        love.graphics.printf(entryText, 0, 120 + i * 40, love.graphics.getWidth(), "center")
    end
    love.graphics.setFont(uiFonts.normal)
    love.graphics.setColor(1, 1, 1, 1)
    -- Draw leave button if on scoreboard
    if showScoreboard then
        local btnW, btnH = 220, 48
        local btnX = (love.graphics.getWidth() - btnW) / 2
        local btnY = love.graphics.getHeight() - 120
        love.graphics.setColor(0.2, 0.8, 0.2, 1)
        love.graphics.rectangle("fill", btnX, btnY, btnW, btnH, 12, 12)
        love.graphics.setColor(0, 0, 0, 1)
        love.graphics.setFont(uiFonts.large)
        love.graphics.printf("Continue", btnX, btnY + 8, btnW, "center")
        love.graphics.setFont(uiFonts.normal)
        love.graphics.setColor(1, 1, 1, 1)
    end
end

-- Utility: Check if all planets are conquered
local function allPlanetsConquered()
    for _, p in ipairs(planets) do
        if not p.conquered then return false end
    end
    return true
end

-- Weapon unlocks
local weaponTypes = {
    {name = "Laser", damage = 5, fireRate = 0.3},
    {name = "Plasma Cannon", damage = 8, fireRate = 0.4},
    {name = "Spread Shot", damage = 4, fireRate = 0.22, spread = true},
    {name = "Missile", damage = 12, fireRate = 0.7, splash = true},
    {name = "Pulse Beam", damage = 7, fireRate = 0.5},
    {name = "Railgun", damage = 16, fireRate = 1.1, pierce = true},
    {name = "Arc Blaster", damage = 6, fireRate = 0.18, arc = true},
    {name = "Flak Cannon", damage = 3, fireRate = 0.13, flak = true},
    {name = "Sniper Beam", damage = 22, fireRate = 1.3, sniper = true},
    {name = "EMP Launcher", damage = 2, fireRate = 0.8, emp = true},
    {name = "Sawblade", damage = 10, fireRate = 0.33, saw = true},
    {name = "Bouncer", damage = 5, fireRate = 0.38, bounce = true}
}
local playerWeaponLevel = 1

-- Enemy ship archetypes
local enemyArchetypes = {
    big_slow = {
        name = "Big Slow",
        maxHealth = 220,
        speed = 110,
        damage = 18,
        fireRate = 1.5,
        w = 54, h = 54,
        color = {1, 0.5, 0.2},
        shape = "rectangle"
    }
}

-- Give player a new weapon after each galaxy
function unlockNextWeapon()
    -- Randomly give a new weapon (not the current one)
    local available = {}
    for i, w in ipairs(weaponTypes) do
        if i ~= playerWeaponLevel then
            table.insert(available, i)
        end
    end
    if #available > 0 then
        local idx = available[math.random(1, #available)]
        playerWeaponLevel = idx
        local w = weaponTypes[playerWeaponLevel]
        playerStats.ship.damage = w.damage
        playerStats.ship.fireRate = w.fireRate
        playerStats.ship.weaponName = w.name
    end
end

-- Generate a new galaxy with more planets and harder enemies
function generateNewGalaxy(initial)
    unlockNextWeapon()
    galaxyBackground = generateGalaxyBackground()
    local numPlanets = 3 + galaxyLevel
    galaxyLevel = galaxyLevel + 1
    planetNames = {
        "Zorath", "Eryndor", "Vexalon", "Thalora", "Cryonix", "Zephyra", "Lunaris", "Aetherion", "Draconis", "Solara",
        "Nebulon", "Quorath", "Xythera", "Orionis", "Pyronix", "Celestara", "Galadorn", "Astralis", "Velocis", "Ignis",
        "Aurion", "Stellara", "Chronos", "Ecliptica", "Novaera", "Polaris", "Syntara", "Lycoris", "Tritonix", "Eldara",
        "Frostara", "Blazara", "Zenthara", "Krythos", "Omnara", "Vortara", "Nyxara", "Phantora", "Luminara", "Oblivion",
        "Ravara", "Spectra", "Xenara", "Abyssara", "Erythion", "Halcyon", "Mystara", "Eosara", "Calythra", "Zyphara"
    }
    -- Shuffle planetNames for this galaxy
    local shuffledNames = {}
    for i, v in ipairs(planetNames) do shuffledNames[i] = v end
    for i = #shuffledNames, 2, -1 do
        local j = math.random(i)
        shuffledNames[i], shuffledNames[j] = shuffledNames[j], shuffledNames[i]
    end
    planets = {}
    local angleStep = (2 * math.pi) / numPlanets
    local centerX, centerY = BASE_WIDTH / 2, BASE_HEIGHT / 2
    local radius = math.min(BASE_WIDTH, BASE_HEIGHT) / 2.5
    local resources = {"quantonium", "zyther_crystals", "plasma_gel"}
    local galaxyName = galaxyNames[((galaxyLevel - 1) % #galaxyNames) + 1]
    for i = 1, numPlanets do
        local angle = angleStep * (i - 1)
        local px = centerX + math.cos(angle) * radius * (0.7 + 0.3 * math.random())
        local py = centerY + math.sin(angle) * radius * (0.7 + 0.3 * math.random())
        local res = resources[(i - 1) % #resources + 1]
        local enemyTypes = {}
        local availableArchetypes = {"big_slow"}
        local nShips = 3 + math.floor(galaxyLevel * 1.5) + math.random(0, galaxyLevel)
        for s = 1, nShips do
            local archetypeKey = availableArchetypes[math.random(1, #availableArchetypes)]
            table.insert(enemyTypes, archetypeKey)
        end
        local enemyHealth = 70 + (galaxyLevel - 1) * 18
        local enemyDamage = 5 + math.floor((galaxyLevel - 1) * 1.5)
        local baseHealth = 200 + (galaxyLevel - 1) * 40
        local baseDamage = 12 + math.floor((galaxyLevel - 1) * 2)
        local planetName = shuffledNames[i] or (galaxyName .. " - Planet " .. i)
        local planet = {
            x = px,
            y = py,
            radius = 18 + math.random(0, 10),
            name = planetName,
            resource = res,
            conquered = false,
            baseDestroyed = false,
            color = {math.random(), math.random(), math.random()},
            enemyConfig = {
                ships = nShips,
                enemyTypes = enemyTypes,
                enemyHealth = enemyHealth,
                enemyDamage = enemyDamage,
                baseHealth = baseHealth,
                baseDamage = baseDamage
            },
            base = {
                health = baseHealth,
                damage = baseDamage,
                isBase = true
            }
        }
        table.insert(planets, planet)
    end
    newGalaxyMessage = "Entering " .. galaxyName .. "!"
    newGalaxyTimer = NEW_GALAXY_MSG_TIME
end

-- Simple collision detection function (AABB)
function checkCollision(obj1, obj2)
    if not obj1 or not obj2 or not obj1.x or not obj2.x or not obj1.y or not obj2.y or not obj1.w or not obj2.w or not obj1.h or not obj2.h then
        return false -- Object missing required properties
    end
    return obj1.x < obj2.x + obj2.w and
           obj1.x + obj1.w > obj2.x and
           obj1.y < obj2.y + obj2.h and
           obj1.y + obj1.h > obj2.y
end

function setupScaling()
    scaleX = love.graphics.getWidth() / BASE_WIDTH
    scaleY = love.graphics.getHeight() / BASE_HEIGHT
end

-- =========================================================================
-- LOVE2D CALLBACKS
-- =========================================================================

function love.load()
    love.window.setTitle("Alien Invaders")
    love.window.setMode(3840, 2160, {resizable = true}) -- Start at 4K and make window resizable

    -- Set up scaling factors for UI and gameplay objects
    setupScaling()

    -- Load fonts for UI scaling
    uiFonts.normal = love.graphics.newFont(18)   -- Smaller font for galaxy/map screen
    uiFonts.large = love.graphics.newFont(36)    -- Large font for combat and headings

    -- TODO: Load assets (images, fonts, sounds) here

    -- Initialize Game States
    initializeMapState()
    -- initializeCombatState() -- Called when entering combat
end

function love.resize(w, h)
    setupScaling()
end

function love.update(dt)
    -- Update logic based on the current game state
    if gameState == "map" then
        updateMapState(dt)
    elseif gameState == "combat" then
        updateCombatState(dt)
    elseif gameState == "harvesting" then
        updateHarvestingState(dt)
    elseif gameState == "traveling" then
        updateTravelingState(dt)
    elseif gameState == "gameover" and isGameOver then
        gameOverTimer = gameOverTimer - dt
        if gameOverTimer <= 0 and not showScoreboard then
            -- Reset everything for a new game
            galaxyLevel = 1
            playerResources = { quantonium = 0, zyther_crystals = 0, plasma_gel = 0 }
            playerStats = {
                ship = {
                    health = 100,
                    maxHealth = 100,
                    speed = 500,
                    damage = 10,
                    fireRate = 0.2,
                    shield = 60,
                    maxShield = 60,
                    shieldRegen = 10,
                    weaponName = weaponTypes[1].name -- Reset weapon name
                },
                armadaSize = 3
            }
            playerWeaponLevel = 1 -- Reset to starting weapon
            playerScore = 0
            isGameOver = false
            initializeMapState()
            currentTargetPlanet = nil -- Also clear selected planet on game restart
            gameState = "map"
        end
    end
end

function love.draw()
    -- Drawing logic based on the current game state
    if gameState == "map" then
        drawMapState()
    elseif gameState == "combat" then
        drawCombatState()
    elseif gameState == "harvesting" then
        drawHarvestingState(dt)
    elseif gameState == "traveling" then
        drawTravelingState(dt)
    elseif gameState == "gameover" then
        drawGameOver()
    end

    -- Draw FPS (optional debug info)
    love.graphics.setColor(0, 1, 0, 1)
    love.graphics.print("FPS: " .. love.timer.getFPS(), 10, love.graphics.getHeight() - 20)
    love.graphics.setColor(1, 1, 1, 1) -- Reset color
end

function love.mousepressed(x, y, button, istouch, presses)
    if button == 1 and combatObjects.player then -- Left click to shoot
        combatObjects.player:shoot(x / scaleX, y / scaleY) -- Adjust for scaling
    end
    if gameState == "gameover" and showScoreboard and button == 1 then
        local btnW, btnH = 220, 48
        local btnX = (love.graphics.getWidth() - btnW) / 2
        local btnY = love.graphics.getHeight() - 120
        if x > btnX and x < btnX + btnW and y > btnY and y < btnY + btnH then
            showScoreboard = false
            -- Reset everything for a new game
            galaxyLevel = 1
            playerResources = { quantonium = 0, zyther_crystals = 0, plasma_gel = 0 }
            playerStats = {
                ship = {
                    health = 100,
                    maxHealth = 100,
                    speed = 500,
                    damage = 10,
                    fireRate = 0.2,
                    shield = 60,
                    maxShield = 60,
                    shieldRegen = 10,
                    weaponName = weaponTypes[1].name
                },
                armadaSize = 3
            }
            playerWeaponLevel = 1
            playerScore = 0
            isGameOver = false
            initializeMapState()
            currentTargetPlanet = nil -- Also clear selected planet on game restart
            gameState = "map"
        end
    else
        if gameState == "map" then
            handleMapMouseInput(x, y, button)
        elseif gameState == "combat" then
            handleCombatMouseInput(x, y, button)
        end
    end
end

function love.keypressed(key, scancode, isrepeat)
     if gameState == "combat" then
        handleCombatKeyInput(key, true) -- true for pressed
     elseif gameState == "map" and key == "escape" then
        love.event.quit() -- Allow quitting from map
     elseif key == "escape" then -- Option to return to map from combat (maybe pause menu later)
        -- For now, let's just instantly go back to map for testing
        print("DEBUG: Esc pressed in combat, returning to map")
        changeState("map")
     end
end

function love.keyreleased(key, scancode)
     if gameState == "combat" then
        handleCombatKeyInput(key, false) -- false for released
     end
end

-- =========================================================================
-- GAME STATE MANAGEMENT
-- =========================================================================

function changeState(newState, ...)
    local args = {...}
    print("Changing state from " .. gameState .. " to " .. newState)

    -- Optional: Add exit logic for the old state here
    if gameState == "combat" then
        clearCombatObjects()
    end

    gameState = newState

    -- Optional: Add entry logic for the new state here
    if newState == "combat" then
        initializeCombatState(args[1]) -- Pass the selected planet
    elseif newState == "harvesting" then
        initializeHarvestingState(args[1]) -- Pass the harvested planet
    elseif newState == "map" then
        -- Reset things if needed when returning to map
        currentTargetPlanet = nil
        clearCombatObjects() -- Clear combat debris when returning
    end
end

function clearCombatObjects()
    combatObjects = {
        player = nil,
        playerArmada = {},
        enemies = {},
        bullets = {}
    }
end

-- =========================================================================
-- MAP STATE
-- =========================================================================
local upgradeMenu = {
    active = false,
    options = {
        { name = "Armada Size", cost = { quantonium = 5 }, action = function() if playerResources.quantonium >= 5 then playerResources.quantonium = playerResources.quantonium - 5; playerStats.armadaSize = playerStats.armadaSize + 1; print("Upgraded Armada Size") else print("Not enough Quantonium") end end },
        { name = "Weapon Damage", cost = { zyther_crystals = 3 }, action = function() if playerResources.zyther_crystals >= 3 then playerResources.zyther_crystals = playerResources.zyther_crystals - 3; playerStats.ship.damage = playerStats.ship.damage + 2; print("Upgraded Weapon Damage") else print("Not enough Zyther Crystals") end end },
        { name = "Shield Capacity", cost = { plasma_gel = 5 }, action = function() if playerResources.plasma_gel >= 5 then playerResources.plasma_gel = playerResources.plasma_gel - 5; playerStats.ship.maxShield = playerStats.ship.maxShield + 20; playerStats.ship.shield = playerStats.ship.maxShield; print("Upgraded Shield Capacity") else print("Not enough Plasma Gel") end end },
        { name = "Shield Regen", cost = { quantonium = 3, plasma_gel = 2 }, action = function() if playerResources.quantonium >= 3 and playerResources.plasma_gel >= 2 then playerResources.quantonium = playerResources.quantonium - 3; playerResources.plasma_gel = playerResources.plasma_gel - 2; playerStats.ship.shieldRegen = playerStats.ship.shieldRegen + 4; print("Upgraded Shield Regen") else print("Not enough resources") end end },
        { name = "Health Upgrade", cost = { zyther_crystals = 4 }, action = function() if playerResources.zyther_crystals >= 4 then playerResources.zyther_crystals = playerResources.zyther_crystals - 4; playerStats.ship.maxHealth = playerStats.ship.maxHealth + 20; playerStats.ship.health = playerStats.ship.maxHealth; print("Upgraded Max Health") else print("Not enough Zyther Crystals") end end },
    }
}

local oldInitializeMapState = initializeMapState
function initializeMapState()
    galaxyBackground = generateGalaxyBackground()
    print("Initializing Map State")
    currentTargetPlanet = nil -- Always clear selected planet on map init
    if galaxyLevel == 1 then
        -- First galaxy, use default planets
        generateNewGalaxy(true)
    else
        generateNewGalaxy(false)
    end
    upgradeMenu.active = false -- Ensure upgrade menu is closed initially
end

function updateMapState(dt)
    -- Show new galaxy message if needed
    if newGalaxyMessage then
        newGalaxyTimer = newGalaxyTimer - dt
        if newGalaxyTimer <= 0 then
            newGalaxyMessage = nil
        end
    end
    -- Currently, map state is mostly static, waiting for input
    -- Could add animations, background scrolling etc. here
end

function drawMapState()
    love.graphics.setBackgroundColor(0.05, 0.05, 0.15)
    love.graphics.push()
    love.graphics.scale(scaleX, scaleY)

    -- Draw clouds/nebulae
    if galaxyBackground and galaxyBackground.clouds then
        for _, cloud in ipairs(galaxyBackground.clouds) do
            love.graphics.setColor(cloud.color)
            love.graphics.ellipse("fill", cloud.cx, cloud.cy, cloud.r*1.2, cloud.r*0.7)
        end
    end
    -- Draw star clusters
    if galaxyBackground and galaxyBackground.clusters then
        for _, cluster in ipairs(galaxyBackground.clusters) do
            -- Soft cluster glow
            love.graphics.setColor(cluster.color)
            love.graphics.circle("fill", cluster.cx, cluster.cy, cluster.r * 1.1)
            -- Stars
            for _, star in ipairs(cluster.stars) do
                love.graphics.setColor(star.color[1], star.color[2], star.color[3], 0.7)
                love.graphics.circle("fill", star.x, star.y, star.size)
            end
        end
    end
    -- Draw scattered stars
    if galaxyBackground and galaxyBackground.scattered then
        for _, star in ipairs(galaxyBackground.scattered) do
            love.graphics.setColor(star.color[1], star.color[2], star.color[3], 0.55)
            love.graphics.circle("fill", star.x, star.y, star.size)
        end
    end
    love.graphics.setColor(1,1,1,1)

    -- Draw Planets (with more realistic look)
    for i, p in ipairs(planets) do
        -- Set color to more grey if conquered
        local planetColor = p.color
        if p.conquered then
            planetColor = {0.25, 0.25, 0.25}
        end
        -- Planet base gradient (radial)
        local segments = 32
        local cx, cy, r = p.x, p.y, p.radius
        for s = segments, 1, -1 do
            local t = s / segments
            local r1 = r * t
            local c = {planetColor[1] * (0.7 + 0.3 * t), planetColor[2] * (0.7 + 0.3 * t), planetColor[3] * (0.7 + 0.3 * t), 1}
            if p.conquered then
                c = {0.25, 0.25, 0.25, 0.7 * t}
            end
            love.graphics.setColor(c)
            love.graphics.circle("fill", cx, cy, r1)
        end
        -- Atmospheric glow
        love.graphics.setColor(p.color[1], p.color[2], p.color[3], 0.18)
        love.graphics.circle("fill", cx, cy, r * 1.18)
        -- Surface bands/spots
        for j = 1, 3 do
            local bandY = cy + r * (math.sin(i + j) * 0.4 + (j-2)*0.18)
            love.graphics.setColor(1, 1, 1, 0.10)
            love.graphics.ellipse("fill", cx, bandY, r * (0.7 - 0.18 * j), r * 0.13)
        end
        -- Polar caps
        love.graphics.setColor(1, 1, 1, 0.13)
        love.graphics.ellipse("fill", cx, cy - r * 0.7, r * 0.32, r * 0.13)
        love.graphics.ellipse("fill", cx, cy + r * 0.7, r * 0.32, r * 0.13)
        -- Optional: ring for some planets
        if i % 3 == 0 then
            love.graphics.setColor(1, 1, 1, 0.10)
            love.graphics.ellipse("line", cx, cy, r * 1.25, r * 0.38, 48)
        end
        -- Draw a little green flag on conquered planets
        if p.conquered then
            local flagX = p.x + p.radius * 0.6
            local flagY = p.y - p.radius * 0.8
            local flagH = p.radius * 0.7
            local flagW = p.radius * 0.5
            -- Flag pole
            love.graphics.setColor(0.2, 0.2, 0.2, 1)
            love.graphics.setLineWidth(2)
            love.graphics.line(flagX, flagY, flagX, flagY + flagH)
            -- Flag cloth
            love.graphics.setColor(0.2, 1, 0.2, 1)
            love.graphics.polygon("fill", flagX, flagY, flagX + flagW, flagY + flagH * 0.18, flagX, flagY + flagH * 0.36)
            love.graphics.setLineWidth(1)
        end
        love.graphics.setColor(1, 1, 1, 1)
        love.graphics.print(p.name, p.x - p.radius, p.y + p.radius + 5)
        love.graphics.print("("..p.resource..")", p.x - p.radius, p.y + p.radius + 20)
        if p == currentTargetPlanet then
            love.graphics.setColor(1, 1, 0, 1)
            love.graphics.circle("line", p.x, p.y, p.radius + 3)
            love.graphics.setColor(1, 1, 1, 1)
        end
    end

    -- Draw Player Resources
    local resY = 10
    love.graphics.setFont(uiFonts.normal)
    love.graphics.print("Resources:", 10, resY)
    resY = resY + 30
    for name, amount in pairs(playerResources) do
        love.graphics.print(name .. ": " .. amount, 10, resY)
        resY = resY + 28
    end

    -- Draw Player Stats
    local statsY = BASE_HEIGHT - 120
    love.graphics.setFont(uiFonts.normal)
    love.graphics.setColor(1, 1, 1)
    love.graphics.print("Player Stats:", 10, statsY)
    statsY = statsY + 22
    love.graphics.print("Score: " .. playerScore, 10, statsY)
    statsY = statsY + 20
    love.graphics.print("Armada Size: " .. (playerStats.armadaSize or 1), 10, statsY)
    statsY = statsY + 20
    love.graphics.print("Weapon Strength: " .. (playerStats.ship.damage or 0), 10, statsY)
    statsY = statsY + 20
    love.graphics.print("Health: " .. (playerStats.ship.health or 0) .. "/" .. (playerStats.ship.maxHealth or 0), 10, statsY)
    statsY = statsY + 20
    love.graphics.print("Shield: " .. (playerStats.ship.shield or 0) .. "/" .. (playerStats.ship.maxShield or 0), 10, statsY)
    love.graphics.setColor(1, 1, 1)

    -- Draw Upgrade Button
    local upgradeButton = { x = BASE_WIDTH - 150, y = 10, w = 140, h = 30 }
    love.graphics.setColor(0.8, 0.8, 0.8)
    love.graphics.rectangle("fill", upgradeButton.x, upgradeButton.y, upgradeButton.w, upgradeButton.h)
    love.graphics.setColor(0, 0, 0)
    love.graphics.setFont(uiFonts.normal)
    love.graphics.printf("Upgrades", upgradeButton.x, upgradeButton.y + 6, upgradeButton.w, "center")
    love.graphics.setColor(1, 1, 1)

    -- Draw Help Button
    local helpButton = { x = BASE_WIDTH - 150, y = 50, w = 140, h = 30 }
    love.graphics.setColor(0.7, 0.7, 1)
    love.graphics.rectangle("fill", helpButton.x, helpButton.y, helpButton.w, helpButton.h)
    love.graphics.setColor(0, 0, 0)
    love.graphics.setFont(uiFonts.normal)
    love.graphics.printf("Help", helpButton.x, helpButton.y + 6, helpButton.w, "center")
    love.graphics.setColor(1, 1, 1)

    -- Draw Upgrade Menu if active
    if upgradeMenu.active then
        local menuW = 480
        local menuH = 220
        local menuX = (BASE_WIDTH - menuW) / 2
        local menuY = 120 -- Place below the top buttons

        -- Ensure the menu doesn't go off the bottom of the screen
        if menuY + menuH > BASE_HEIGHT then
            menuY = BASE_HEIGHT - menuH - 10
        end

        love.graphics.setColor(0.2, 0.2, 0.2, 1) -- Not transparent
        love.graphics.rectangle("fill", menuX, menuY, menuW, menuH)
        love.graphics.setColor(1, 1, 1)
        love.graphics.setFont(uiFonts.normal)
        love.graphics.print("Upgrade Menu", menuX + 10, menuY + 5)
        local optionY = menuY + 30
        for i, opt in ipairs(upgradeMenu.options) do
            local costStr = ""
            local canAfford = true
            for res, amount in pairs(opt.cost) do
                costStr = costStr .. amount .. " " .. res .. " "
                if not playerResources[res] or playerResources[res] < amount then
                    canAfford = false
                end
            end
            local text = string.format("%d. %s (%s)", i, opt.name, costStr)
            opt.btn = { x = menuX + 10, y = optionY, w = menuW - 20, h = 32 }
            if canAfford then
                love.graphics.setColor(0.2, 0.8, 0.2, 1) -- green
            else
                love.graphics.setColor(0.9, 0.2, 0.2, 1) -- red
            end
            love.graphics.rectangle("fill", opt.btn.x, opt.btn.y, opt.btn.w, opt.btn.h)
            love.graphics.setColor(1,1,1)
            love.graphics.print(text, opt.btn.x + 3, opt.btn.y + 6)
            optionY = optionY + 36
        end
    end

    -- Draw Help Menu if active
    if helpMenu and helpMenu.active then
        local menuX = BASE_WIDTH / 2 - 250
        local menuY = BASE_HEIGHT / 2 - 180
        local menuW = 500
        local menuH = 320
        love.graphics.setColor(0.1, 0.1, 0.2, 0.95)
        love.graphics.rectangle("fill", menuX, menuY, menuW, menuH, 12, 12)
        love.graphics.setColor(1, 1, 1)
        love.graphics.setFont(uiFonts.large)
        love.graphics.printf("Help", menuX, menuY + 10, menuW, "center")
        love.graphics.setFont(uiFonts.normal)
        local helpText = [[
[W][A][S][D] or Arrow Keys: Move ship (combat)
Mouse Left Click: Shoot (combat)
ESC: Quit (map) or Return to Map (combat)
Click planet: Select target
Click ATTACK!: Start combat
Click Upgrades: Open upgrade menu
Click Help: Show this help
        ]]
        love.graphics.printf(helpText, menuX + 20, menuY + 80, menuW - 40, "left")
        love.graphics.setColor(1, 0.5, 0.5)
        love.graphics.printf("Click anywhere to close", menuX, menuY + menuH - 40, menuW, "center")
        love.graphics.setColor(1, 1, 1)
    end

    -- Draw 'Attack' button if a planet is selected
    if currentTargetPlanet and not currentTargetPlanet.conquered then
        local attackButton = { x = currentTargetPlanet.x - 50, y = currentTargetPlanet.y + currentTargetPlanet.radius + 40, w = 100, h = 36 }
        love.graphics.setColor(1, 0, 0)
        love.graphics.rectangle("fill", attackButton.x, attackButton.y, attackButton.w, attackButton.h, 8, 8)
        love.graphics.setColor(1, 1, 1)
        love.graphics.setFont(uiFonts.normal)
        love.graphics.printf("ATTACK!", attackButton.x, attackButton.y + 8, attackButton.w, "center")
        love.graphics.setColor(1, 1, 1)
    end

    -- Draw new galaxy message if present
    if newGalaxyMessage then
        love.graphics.setColor(1, 1, 0)
        love.graphics.setFont(uiFonts.large)
        love.graphics.printf(newGalaxyMessage, 0, BASE_HEIGHT / 2 - 80, BASE_WIDTH, "center")
        love.graphics.setFont(uiFonts.normal)
        love.graphics.setColor(1, 1, 1)
    end

    love.graphics.setFont(uiFonts.normal)
    love.graphics.pop()
end

-- Help menu state
helpMenu = { active = false }

function handleMapMouseInput(x, y, button)
    x = x / scaleX
    y = y / scaleY

    if helpMenu.active then
        helpMenu.active = false
        return
    end

    if button == 1 then
        local upgradeButton = { x = BASE_WIDTH - 150, y = 10, w = 140, h = 30 }
        local helpButton = { x = BASE_WIDTH - 150, y = 50, w = 140, h = 30 }
        if x > upgradeButton.x and x < upgradeButton.x + upgradeButton.w and y > upgradeButton.y and y < upgradeButton.y + upgradeButton.h then
            upgradeMenu.active = not upgradeMenu.active
            return
        end
        if x > helpButton.x and x < helpButton.x + helpButton.w and y > helpButton.y and y < helpButton.y + helpButton.h then
            helpMenu.active = true
            return
        end

        -- Check Upgrade Options if menu active
        if upgradeMenu.active then
            for i, opt in ipairs(upgradeMenu.options) do
                if opt.btn and x > opt.btn.x and x < opt.btn.x + opt.btn.w and y > opt.btn.y and y < opt.btn.y + opt.btn.h then
                    opt.action()
                    return
                end
            end
            local menuX = BASE_WIDTH - 220; local menuY = upgradeButton.y + upgradeButton.h + 5
            local menuW = 210; local menuH = 150
            if not (x > menuX and x < menuX + menuW and y > menuY and y < menuY + menuH) then
                if not (x > upgradeButton.x and x < upgradeButton.x + upgradeButton.w and y > upgradeButton.y and y < upgradeButton.y + upgradeButton.h) then
                    upgradeMenu.active = false
                end
            end
        end

        local planetClicked = nil
        for i, p in ipairs(planets) do
            local distSq = (x - p.x)^2 + (y - p.y)^2
            if distSq < p.radius^2 then
                planetClicked = p
                break
            end
        end

        if planetClicked then
            if not planetClicked.conquered then
                currentTargetPlanet = planetClicked
                upgradeMenu.active = false
                print("Selected planet:", currentTargetPlanet.name)
            else
                print("Planet already conquered:", planetClicked.name)
                currentTargetPlanet = nil
            end
        else
            if currentTargetPlanet and not currentTargetPlanet.conquered then
                local attackButton = { x = currentTargetPlanet.x - 50, y = currentTargetPlanet.y + currentTargetPlanet.radius + 40, w = 100, h = 36 }
                if x > attackButton.x and x < attackButton.x + attackButton.w and y > attackButton.y and y < attackButton.y + attackButton.h then
                    print("Attacking", currentTargetPlanet.name)
                    changeState("combat", currentTargetPlanet)
                    return
                end
            end
            if not upgradeMenu.active then
                currentTargetPlanet = nil
            end
        end
    end
end

-- =========================================================================
-- COMBAT STATE
-- =========================================================================
-- Track if player is holding the fire button (space)
local playerHoldingFire = false

-- Add aiming direction for the player
local playerAim = { x = 0, y = -1 } -- Default aim up

-- Spin state for the player
local playerSpinning = false
local spinTimer = 0
local SPIN_DURATION = 0.7
local SPIN_SPEED = 18 * math.pi -- fast spin

-- Add health boosters to the combat state
local healthBoosters = {}

-- Simple Ship Class (Using tables)
local Ship = {}
Ship.__index = Ship

function Ship.new(x, y, img, stats, type)
    local instance = setmetatable({}, Ship)
    instance.x = x
    instance.y = y
    instance.w = 32 -- Placeholder size, use image dimensions later
    instance.h = 32 -- Placeholder size
    instance.img = img -- Placeholder for love.graphics.image
    instance.stats = stats -- Health, speed, damage, fireRate, etc.
    instance.health = stats.maxHealth or 100
    instance.speed = stats.speed or 150
    instance.fireRate = stats.fireRate or 1
    instance.fireCooldown = 0
    instance.type = type -- "player", "player_ai", "enemy_ship", "base"
    instance.target = nil -- For AI
    instance.moveInput = { x = 0, y = 0 } -- For player control
    instance.rotation = 0 -- New: rotation in radians
    instance.shield = stats.maxShield or 0
    instance.maxShield = stats.maxShield or 0
    instance.shieldRegen = stats.shieldRegen or 0
    -- For enemy AI: add random movement state
    if type == "enemy_ship" then
        instance.ai = {
            mode = "random", -- or "chase"
            timer = math.random(1, 3),
            dir = { x = math.random() * 2 - 1, y = math.random() * 2 - 1 }
        }
    end
    return instance
end

function Ship:update(dt)
    if self.type == "player_ai" then
        -- Assign a unique formation slot for each armada ship
        local myIndex = nil
        for i, ship in ipairs(combatObjects.playerArmada) do
            if ship == self then myIndex = i break end
        end
        -- Target nearest enemy
        local minDist, target = math.huge, nil
        for _, enemy in ipairs(combatObjects.enemies) do
            local dx, dy = enemy.x - self.x, enemy.y - self.y
            local dist = math.sqrt(dx * dx + dy * dy)
            if dist < minDist then
                minDist = dist
                target = enemy
            end
        end
        local tx, ty = nil, nil
        if target then
            tx, ty = target.x, target.y
        end
        -- Formation: spread ships in a circle around the target
        local formationRadius = 80
        local n = #combatObjects.playerArmada
        local angle = 0
        if myIndex and n > 1 then
            angle = (2 * math.pi) * ((myIndex - 1) / n)
        end
        local offsetX, offsetY = 0, 0
        if tx and ty then
            offsetX = math.cos(angle) * formationRadius
            offsetY = math.sin(angle) * formationRadius
        end
        -- Desired position is around the target, or just follow if no target
        local desiredX, desiredY
        if tx and ty then
            desiredX = tx + offsetX
            desiredY = ty + offsetY
        else
            desiredX = self.x
            desiredY = self.y
        end
        -- Move toward desired position
        local dx, dy = desiredX - self.x, desiredY - self.y
        local dist = math.sqrt(dx * dx + dy * dy)
        local moveX, moveY = 0, 0
        if dist > 2 then -- Only move if not close enough
            moveX = dx / dist
            moveY = dy / dist
        end
        -- Strong separation from other armada ships
        local sepX, sepY = 0, 0
        local separationDist = 48
        local separationForce = 2.5
        for _, other in ipairs(combatObjects.playerArmada) do
            if other ~= self then
                local odx = self.x - other.x
                local ody = self.y - other.y
                local odist = math.sqrt(odx*odx + ody*ody)
                if odist > 0 and odist < separationDist then
                    local force = (separationDist - odist) / separationDist
                    sepX = sepX + (odx / odist) * force
                    sepY = sepY + (ody / odist) * force
                end
            end
        end
        -- Combine movement and separation
        moveX = moveX + sepX * separationForce
        moveY = moveY + sepY * separationForce
        -- Normalize
        local len = math.sqrt(moveX^2 + moveY^2)
        if len > 0 then
            moveX = moveX / len
            moveY = moveY / len
        end
        self.x = self.x + moveX * self.speed * dt
        self.y = self.y + moveY * self.speed * dt
        -- Clamp position to screen bounds
        self.x = math.max(0, math.min(love.graphics.getWidth() - self.w, self.x))
        self.y = math.max(0, math.min(love.graphics.getHeight() - self.h, self.y))
        -- Smoothly rotate toward movement direction
        if moveX ~= 0 or moveY ~= 0 then
            local desiredRot = math.atan2(moveY, moveX)
            local rotDiff = desiredRot - (self.rotation or 0)
            while rotDiff > math.pi do rotDiff = rotDiff - 2 * math.pi end
            while rotDiff < -math.pi do rotDiff = rotDiff + 2 * math.pi end
            local rotSpeed = 7.5
            self.rotation = (self.rotation or 0) + math.max(-rotSpeed * dt, math.min(rotSpeed * dt, rotDiff))
        end
        -- Fire at the target if in range
        if target then
            local tdx, tdy = target.x - self.x, target.y - self.y
            local tdist = math.sqrt(tdx*tdx + tdy*tdy)
            if self.fireCooldown <= 0 and tdist < 400 then
                self:shoot(target.x, target.y)
            end
        end
    elseif self.type == "player" then
        self.x = self.x + self.moveInput.x * self.speed * dt
        self.y = self.y + self.moveInput.y * self.speed * dt
        -- Clamp position to screen bounds (basic)
        self.x = math.max(0, math.min(love.graphics.getWidth() - self.w, self.x))
        self.y = math.max(0, math.min(love.graphics.getHeight() - self.h, self.y))
        -- Update rotation based on movement direction
        if self.moveInput.x ~= 0 or self.moveInput.y ~= 0 then
            self.rotation = math.atan2(self.moveInput.y, self.moveInput.x)
        end
    elseif self.type == "player_ai" or self.type == "enemy_ship" then
        -- Formation targeting for player_ai: assign each ship a unique offset around the target
        local tx, ty
        local formationOffsetX, formationOffsetY = 0, 0
        if self.type == "player_ai" then
            -- Target nearest enemy
            local minDist, target = math.huge, nil
            for _, enemy in ipairs(combatObjects.enemies) do
                local dx, dy = enemy.x - self.x, enemy.y - self.y
                local dist = math.sqrt(dx * dx + dy * dy)
                if dist < minDist then
                    minDist = dist
                    target = enemy
                end
            end
            if target then
                tx, ty = target.x, target.y
                -- Move towards the target
                local dx, dy = tx - self.x, ty - self.y
                local dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0 then
                    self.moveInput.x = dx / dist
                    self.moveInput.y = dy / dist
                end
                -- Fire at the target if in range
                if self.fireCooldown <= 0 and dist < 400 then
                    self:shoot(tx, ty)
                end
            end
        else
            -- Target player
            if combatObjects.player then tx, ty = combatObjects.player.x, combatObjects.player.y end
        end
        local vx, vy = 0, 0
        if tx and ty then
            local dx, dy = tx - self.x, ty - self.y
            local dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0 then
                vx = dx / dist
                vy = dy / dist
            end
        end
        -- Simple avoidance: don't overlap with same-type ships
        local ships = (self.type == "player_ai") and combatObjects.playerArmada or combatObjects.enemies
        for _, other in ipairs(ships) do
            if other ~= self then
                local dx = other.x - self.x
                local dy = other.y - self.y
                local dist = math.sqrt(dx*dx + dy*dy)
                -- Reduce jitter: only avoid if much closer than minDist
                local minDist = (self.type == "player_ai") and 22 or 36
                if dist > 0 and dist < minDist * 0.85 then
                    vx = vx - (dx / dist) * (minDist - dist) * 0.08
                    vy = vy - (dy / dist) * (minDist - dist) * 0.08
                end
            end
        end
        -- Normalize
        local vlen = math.sqrt(vx*vx + vy*vy)
        if vlen > 0 then
            vx = vx / vlen
            vy = vy / vlen
        end
        self.x = self.x + vx * self.speed * dt
        self.y = self.y + vy * self.speed * dt
        -- Clamp to screen
        self.x = math.max(0, math.min(love.graphics.getWidth() - self.w, self.x))
        self.y = math.max(0, math.min(love.graphics.getHeight() - self.h, self.y))
        -- Smoothly rotate toward movement direction
        if vx ~= 0 or vy ~= 0 then
            local desiredRot = math.atan2(vy, vx)
            local rotDiff = desiredRot - (self.rotation or 0)
            -- Keep shortest rotation direction
            while rotDiff > math.pi do rotDiff = rotDiff - 2 * math.pi end
            while rotDiff < -math.pi do rotDiff = rotDiff + 2 * math.pi end
            local rotSpeed = 7.5 -- radians per second, adjust for snappiness
            self.rotation = (self.rotation or 0) + math.max(-rotSpeed * dt, math.min(rotSpeed * dt, rotDiff))
        end
        -- Fire if in range
        if self.type == "player_ai" and tx and ty then
            local dx, dy = tx - self.x, ty - self.y
            local dist = math.sqrt(dx*dx + dy*dy)
            if self.fireCooldown <= 0 and dist < 400 then
                self:shoot(tx, ty)
            end
        elseif self.type == "enemy_ship" then
            -- Enemy AI: alternate between random movement and chasing player
            if not self.ai then
                self.ai = { mode = "random", timer = math.random(1, 3), dir = { x = math.random() * 2 - 1, y = math.random() * 2 - 1 } }
            end
            self.ai.timer = self.ai.timer - dt
            if self.ai.timer <= 0 then
                if self.ai.mode == "random" and math.random() < 0.5 then
                    self.ai.mode = "chase"
                    self.ai.timer = math.random(1, 2)
                else
                    self.ai.mode = "random"
                    self.ai.timer = math.random(1, 3)
                    local angle = math.random() * 2 * math.pi
                    self.ai.dir.x = math.cos(angle)
                    self.ai.dir.y = math.sin(angle)
                end
            end
            local moveX, moveY = 0, 0
            if self.ai.mode == "chase" and combatObjects.player then
                local dx = combatObjects.player.x - self.x
                local dy = combatObjects.player.y - self.y
                local dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0 then
                    moveX = dx / dist
                    moveY = dy / dist
                end
            else
                moveX = self.ai.dir.x
                moveY = self.ai.dir.y
            end
            -- Add a little random jitter
            moveX = moveX + (math.random() - 0.5) * 0.2
            moveY = moveY + (math.random() - 0.5) * 0.2
            -- Normalize
            local len = math.sqrt(moveX^2 + moveY^2)
            if len > 0 then
                moveX = moveX / len
                moveY = moveY / len
            end
            self.x = self.x + moveX * self.speed * dt
            self.y = self.y + moveY * self.speed * dt
            -- Clamp position to screen bounds
            self.x = math.max(0, math.min(love.graphics.getWidth() - self.w, self.x))
            self.y = math.max(0, math.min(love.graphics.getHeight() - self.h, self.y))
            -- Smoothly rotate toward movement direction
            if moveX ~= 0 or moveY ~= 0 then
                local desiredRot = math.atan2(moveY, moveX)
                local rotDiff = desiredRot - (self.rotation or 0)
                while rotDiff > math.pi do rotDiff = rotDiff - 2 * math.pi end
                while rotDiff < -math.pi do rotDiff = rotDiff + 2 * math.pi end
                local rotSpeed = 7.5
                self.rotation = (self.rotation or 0) + math.max(-rotSpeed * dt, math.min(rotSpeed * dt, rotDiff))
            end
            -- Fire at player if in range
            if combatObjects.player then
                local dx = combatObjects.player.x - self.x
                local dy = combatObjects.player.y - self.y
                local dist = math.sqrt(dx * dx + dy * dy)
                if self.fireCooldown <= 0 and dist < 400 then
                    self:shoot(combatObjects.player.x, combatObjects.player.y)
                end
            end
        end
    end

    -- Add shield regeneration logic
    if self.shield and self.maxShield and self.shield < self.maxShield and self.shieldRegen and self.shieldRegen > 0 then
        self.shield = math.min(self.maxShield, self.shield + (self.shieldRegen * dt))
    end

    -- Update cooldowns
    if self.fireCooldown > 0 then
        self.fireCooldown = self.fireCooldown - dt
    end
end

function Ship:draw()
    love.graphics.push()
    -- Draw ship with rotation around its center
    love.graphics.translate(self.x + self.w / 2, self.y + self.h / 2)
    love.graphics.rotate(self.rotation)

    if self.type == "enemy_ship" and self.archetype then
        love.graphics.setColor(self.archetype.color)
        if self.archetype.shape == "rectangle" then
            love.graphics.rectangle("fill", -self.w/2, -self.h/2, self.w, self.h, 8, 8)
        elseif self.archetype.shape == "circle" then
            love.graphics.circle("fill", 0, 0, self.w / 2)
        elseif self.archetype.shape == "hexagon" then
            local points = {}
            for i = 0, 5 do
                local angle = math.rad(i * 60)
                local px = math.cos(angle) * self.w / 2
                local py = math.sin(angle) * self.h / 2
                table.insert(points, px)
                table.insert(points, py)
            end
            love.graphics.polygon("fill", points)
        elseif self.archetype.shape == "diamond" then
            local points = {
                0, -self.h / 2,
                -self.w / 2, 0,
                0, self.h / 2,
                self.w / 2, 0
            }
            love.graphics.polygon("fill", points)
        elseif self.archetype.shape == "octagon" then
            local points = {}
            for i = 0, 7 do
                local angle = math.rad(i * 45)
                local px = math.cos(angle) * self.w / 2
                local py = math.sin(angle) * self.h / 2
                table.insert(points, px)
                table.insert(points, py)
            end
            love.graphics.polygon("fill", points)
        else
            -- Default: triangle
            local base = self.w
            local height = self.h
            local points = {
                0, -height / 2,
                -base / 2, height / 2,
                base / 2, height / 2
            }
            love.graphics.polygon("fill", points)
        end
    else
        -- Triangular ship points (isosceles triangle)
        local base = self.w
        local height = self.h
        local points = {
            0, -height / 2,           -- Tip (front)
            -base / 2, height / 2,    -- Left base
            base / 2, height / 2      -- Right base
        }

        -- 3D shading: darker base, lighter tip
        if self.type == "player" then
            love.graphics.setColor(0, 1, 0) -- Main color
        elseif self.type == "player_ai" then
            love.graphics.setColor(0, 0.7, 0.7)
        elseif self.type == "enemy_ship" then
            love.graphics.setColor(1, 0, 0)
        elseif self.type == "base" then
            love.graphics.setColor(0.2, 1, 0.2)
        end

        -- Draw main triangle
        love.graphics.polygon("fill", points)

        -- Draw shaded left side
        love.graphics.setColor(0.2, 0.2, 0.2, 0.5)
        love.graphics.polygon("fill",
            0, -height / 2,
            -base / 2, height / 2,
            0, height / 2 * 0.7
        )

        -- Draw shaded right side
        love.graphics.setColor(1, 1, 1, 0.15)
        love.graphics.polygon("fill",
            0, -height / 2,
            base / 2, height / 2,
            0, height / 2 * 0.7
        )
    end

    love.graphics.setColor(1, 1, 1)
    love.graphics.pop()

    -- Draw health bar (simple)
    local barW = self.w
    local barH = 5
    local barY = self.y - barH - 2
    local healthRatio = self.health / (self.stats.maxHealth or 100)
    love.graphics.setColor(0.5, 0, 0)
    love.graphics.rectangle("fill", self.x, barY, barW, barH)
    love.graphics.setColor(0, 1, 0)
    love.graphics.rectangle("fill", self.x, barY, barW * healthRatio, barH)
    -- Draw shield bar above health if present
    if self.maxShield and self.maxShield > 0 then
        local shieldRatio = (self.shield or 0) / self.maxShield
        local shieldBarY = barY - barH - 2
        love.graphics.setColor(0.2, 0.7, 1)
        love.graphics.rectangle("fill", self.x, shieldBarY, barW * shieldRatio, barH)
        love.graphics.setColor(0.1, 0.3, 0.5)
        love.graphics.rectangle("line", self.x, shieldBarY, barW, barH)
    end
    love.graphics.setColor(1, 1, 1)
end

function Ship:shoot(targetX, targetY)
    if self.fireCooldown <= 0 then
        local weapon = weaponTypes[playerWeaponLevel] or {name="Laser", damage=5}
        self.fireCooldown = self.fireRate
        local px = self.x + self.w / 2
        local py = self.y + self.h / 2
        local dx = targetX - px
        local dy = targetY - py
        local dist = math.sqrt(dx * dx + dy * dy)
        local dirX, dirY = 0, 0
        if dist > 0 then
            dirX = dx / dist
            dirY = dy / dist
        else
            dirY = -1 -- Default direction if no target
        end
        table.insert(combatObjects.bullets, {
            x = px - 2, y = py - 2, w = 4, h = 8,
            vx = dirX * 400, vy = dirY * 400,
            damage = weapon.damage, ownerType = self.type
        })
    end
end

function Ship:takeDamage(amount)
    if self.shield and self.shield > 0 then
        local shieldAbsorbed = math.min(self.shield, amount)
        self.shield = self.shield - shieldAbsorbed
        amount = amount - shieldAbsorbed
    end
    self.health = self.health - amount
    print(self.type, "took", amount, "damage. Health:", self.health)
    if self.health <= 0 then
        return true -- Is destroyed
    end
    return false -- Not destroyed
end

-- Combat State Functions
function initializeCombatState(planet)
    print("Initializing Combat State for planet:", planet.name)
    clearCombatObjects()

    -- Initialize player and armada
    combatObjects.player = Ship.new(BASE_WIDTH / 2, BASE_HEIGHT / 2, nil, playerStats.ship, "player")

    -- Spread formation for player AI ships
    local spreadRadius = 50
    local angleStep = (2 * math.pi) / playerStats.armadaSize
    for i = 1, playerStats.armadaSize do
        local angle = angleStep * (i - 1)
        local x = combatObjects.player.x + math.cos(angle) * spreadRadius
        local y = combatObjects.player.y + math.sin(angle) * spreadRadius
        table.insert(combatObjects.playerArmada, Ship.new(x, y, nil, playerStats.ship, "player_ai"))
    end

    -- Initialize enemy ships
    for _, enemyType in ipairs(planet.enemyConfig.enemyTypes) do
        local archetype = enemyArchetypes[enemyType]
        if archetype then
            local x = math.random(100, BASE_WIDTH - 100)
            local y = math.random(100, BASE_HEIGHT - 100)
            local enemy = Ship.new(x, y, nil, archetype, "enemy_ship")
            enemy.archetype = archetype -- Store the archetype for rendering
            table.insert(combatObjects.enemies, enemy)
        end
    end
end

function updateCombatState(dt)
    -- Update Player
    if combatObjects.player then
        combatObjects.player:update(dt)
        -- Continuous fire if space is held
        if playerHoldingFire then
            -- Shoot in aim direction
            local px = combatObjects.player.x + combatObjects.player.w / 2
            local py = combatObjects.player.y + combatObjects.player.h / 2
            local aimX = px + (playerAim.x * 100)
            local aimY = py + (playerAim.y * 100)
            combatObjects.player:shoot(aimX, aimY)
        end
        -- Handle spinning
        if playerSpinning then
            combatObjects.player.rotation = (combatObjects.player.rotation or 0) + SPIN_SPEED * dt
            spinTimer = spinTimer - dt
            if spinTimer <= 0 then
                playerSpinning = false
            end
        end
    end

    -- Update Player AI Armada
    for i = #combatObjects.playerArmada, 1, -1 do
        local ship = combatObjects.playerArmada[i]
        ship:update(dt)
        if ship.health <= 0 then -- Check if destroyed (though AI might not take damage yet)
            table.remove(combatObjects.playerArmada, i)
        end
    end

    -- Update Enemies
    for i = #combatObjects.enemies, 1, -1 do
        local enemy = combatObjects.enemies[i]
        enemy:update(dt)
        
        -- Enemy collision avoidance: push away from other enemies
        for j, other in ipairs(combatObjects.enemies) do
            if enemy ~= other then
                local dx = (enemy.x + enemy.w/2) - (other.x + other.w/2)
                local dy = (enemy.y + enemy.h/2) - (other.y + other.h/2)
                local dist = math.sqrt(dx*dx + dy*dy)
                local minDist = (enemy.w + other.w) * 0.5 * 0.85
                if dist > 0 and dist < minDist then
                    local push = (minDist - dist) * 0.5
                    local nx, ny = dx / dist, dy / dist
                    enemy.x = enemy.x + nx * push
                    enemy.y = enemy.y + ny * push
                    other.x = other.x - nx * push
                    other.y = other.y - ny * push
                end
            end
        end
        -- Check if destroyed is handled below in collision checks
    end

    -- Update Bullets
    for i = #combatObjects.bullets, 1, -1 do
        local b = combatObjects.bullets[i]
        b.x = b.x + b.vx * dt
        b.y = b.y + b.vy * dt
        -- Remove bullets going off-screen
        if b.y < -b.h or b.y > love.graphics.getHeight() or b.x < -b.w or b.x > love.graphics.getWidth() then
            table.remove(combatObjects.bullets, i)
        else
            -- Bullet Collision Detection
            if b.ownerType == "player" or b.ownerType == "player_ai" then
                -- Check collision with enemies
                for j = #combatObjects.enemies, 1, -1 do
                    local enemy = combatObjects.enemies[j]
                    if checkCollision(b, enemy) then
                        print("Enemy hit!")
                        local destroyed = enemy:takeDamage(b.damage)
                        table.remove(combatObjects.bullets, i) -- Remove bullet on hit
                        if destroyed then
                            print("Enemy destroyed!")
                            table.remove(combatObjects.enemies, j)
                            if b.ownerType == "player" or b.ownerType == "player_ai" then
                                -- Add score based on enemy type
                                local scoreAdd = 100
                                if enemy.isBase then scoreAdd = 500 end
                                playerScore = playerScore + scoreAdd
                            end
                        end
                        goto next_bullet -- Stop checking this bullet against other enemies
                    end
                end
            elseif b.ownerType == "enemy_ship" or b.ownerType == "base" then
                 -- Check collision with player
                 if combatObjects.player and checkCollision(b, combatObjects.player) then
                      print("Player hit!")
                      local destroyed = combatObjects.player:takeDamage(b.damage)
                      table.remove(combatObjects.bullets, i)
                      if destroyed then
                           print("PLAYER DESTROYED! GAME OVER")
                           combatObjects.player = nil
                           triggerGameOver()
                      end
                      goto next_bullet
                 end
                 -- Check collision with player AI ships
                 for j = #combatObjects.playerArmada, 1, -1 do
                     local aiShip = combatObjects.playerArmada[j]
                     if checkCollision(b, aiShip) then
                          print("Player AI hit!")
                          local destroyed = aiShip:takeDamage(b.damage)
                          table.remove(combatObjects.bullets, i)
                          if destroyed then
                               print("Player AI destroyed!")
                               table.remove(combatObjects.playerArmada, j)
                          end
                          goto next_bullet
                     end
                 end
            end
        end
        ::next_bullet::
    end

    -- Check for player collision with health boosters
    if combatObjects.player then
        for _, booster in ipairs(healthBoosters) do
            if not booster.collected then
                local dx = (combatObjects.player.x + combatObjects.player.w/2) - booster.x
                local dy = (combatObjects.player.y + combatObjects.player.h/2) - booster.y
                local dist = math.sqrt(dx*dx + dy*dy)
                if dist < booster.r + combatObjects.player.w/2 then
                    booster.collected = true
                    -- Heal the player (20 health, but not above max)
                    combatObjects.player.health = math.min(combatObjects.player.stats.maxHealth or 100, combatObjects.player.health + 20)
                end
            end
        end
    end

    -- Update radio message timer
    if radioMessageTimer > 0 then
        radioMessageTimer = radioMessageTimer - dt
        if radioMessageTimer <= 0 then
            radioMessage = nil
        end
    end

    -- Check Win Condition: all enemies and the base must be destroyed
    local baseExists = false
    local shipsExist = false
    
    for _, enemy in ipairs(combatObjects.enemies) do
        if enemy.isBase then
            baseExists = true
        else
            shipsExist = true
        end
    end
    
    if not baseExists and not shipsExist and combatObjects.player then
        print("VICTORY! All enemies and base destroyed on", currentTargetPlanet.name)
        currentTargetPlanet.baseDestroyed = true
        changeState("harvesting", currentTargetPlanet)
    end
end

function drawCombatState()
    -- Draw planet background first
    love.graphics.setBackgroundColor(0.1, 0.1, 0.1)
    love.graphics.push()
    love.graphics.scale(scaleX, scaleY)
    -- Draw a large planet (circle) in the background
    local planetRadius = BASE_HEIGHT * 0.7
    local planetX = BASE_WIDTH / 2
    local planetY = BASE_HEIGHT * 0.85
    love.graphics.setColor(0.2, 0.4, 0.8, 0.7) -- Soft blue planet
    love.graphics.circle("fill", planetX, planetY, planetRadius)
    -- Add a lighter highlight for depth
    love.graphics.setColor(0.5, 0.7, 1, 0.18)
    love.graphics.circle("fill", planetX - planetRadius * 0.3, planetY - planetRadius * 0.3, planetRadius * 0.5)
    -- Draw city lights (clusters of rectangles and dots) at fixed positions
    local citySeeds = {
        {angle=12, dist=0.78}, {angle=38, dist=0.82}, {angle=65, dist=0.74}, {angle=95, dist=0.85},
        {angle=120, dist=0.77}, {angle=150, dist=0.81}, {angle=185, dist=0.75}, {angle=210, dist=0.83},
        {angle=245, dist=0.79}, {angle=275, dist=0.76}, {angle=310, dist=0.84}, {angle=340, dist=0.73}
    }
    for _, seed in ipairs(citySeeds) do
        local angle = math.rad(seed.angle)
        local dist = planetRadius * seed.dist
        local cx = planetX + math.cos(angle) * dist
        local cy = planetY + math.sin(angle) * dist * 0.7
        -- Draw a city cluster: a few rectangles and dots (fixed offsets)
        for j = 1, 4 do
            local ox = (j-2.5)*8
            local oy = ((j%2)*2-1)*4
            local w = 10 + (j%2)*4
            local h = 6 + ((j+1)%2)*3
            love.graphics.setColor(1, 1, 0.7, 0.28)
            love.graphics.rectangle("fill", cx + ox, cy + oy, w, h, 2, 2)
        end
        -- Draw some dots for lights (fixed offsets)
        for j = 1, 5 do
            local ox = (j-3)*7
            local oy = ((j%2)*2-1)*3
            love.graphics.setColor(1, 1, 0.5, 0.22)
            love.graphics.circle("fill", cx + ox, cy + oy, 2)
        end
    end
    love.graphics.setColor(1, 1, 1, 1)
    love.graphics.pop()

    love.graphics.setFont(uiFonts.large)
    -- Draw Player
    if combatObjects.player then
        combatObjects.player:draw()
    end

    -- Draw Player AI Armada
    for _, ship in ipairs(combatObjects.playerArmada) do
        ship:draw()
    end

    -- Draw Enemies
    for _, enemy in ipairs(combatObjects.enemies) do
        if enemy.isBase then
            -- Draw base using the same style as ships (isosceles triangle with shading)
            love.graphics.push()
            local cx = enemy.x + enemy.w / 2
            local cy = enemy.y + enemy.h / 2
            love.graphics.translate(cx, cy)
            love.graphics.rotate(enemy.rotation or 0)
            local base = enemy.w
            local height = enemy.h
            local points = {
                0, -height / 2,           -- Tip (front)
                -base / 2, height / 2,    -- Left base
                base / 2, height / 2      -- Right base
            }
            love.graphics.setColor(0.2, 1, 0.2, 1)
            love.graphics.polygon("fill", points)
            -- Shaded left side
            love.graphics.setColor(0.2, 0.2, 0.2, 0.5)
            love.graphics.polygon("fill", 0, -height / 2, -base / 2, height / 2, 0, height / 2 * 0.7)
            -- Shaded right side
            love.graphics.setColor(1, 1, 1, 0.15)
            love.graphics.polygon("fill", 0, -height / 2, base / 2, height / 2, 0, height / 2 * 0.7)
            love.graphics.setColor(1, 1, 1)
            love.graphics.pop()
            -- Draw health bar above the base
            local barW = enemy.w
            local barH = 8
            local barX = enemy.x
            local barY = enemy.y - barH - 8
            local healthRatio = enemy.health / (enemy.stats.maxHealth or 200)
            love.graphics.setColor(0.5, 0, 0)
            love.graphics.rectangle("fill", barX, barY, barW, barH)
            love.graphics.setColor(0, 1, 0)
            love.graphics.rectangle("fill", barX, barY, barW * healthRatio, barH)
            love.graphics.setColor(1, 1, 1, 1)
        else
            enemy:draw()
        end
    end

    -- Draw Bullets
    for _, b in ipairs(combatObjects.bullets) do
        if b.color then
            love.graphics.setColor(b.color)
        elseif b.ownerType == "enemy_ship" or b.ownerType == "base" then
            love.graphics.setColor(1, 0, 0) -- Enemy attacks are now red
        else
            love.graphics.setColor(0.5, 1, 1)
        end
        love.graphics.rectangle("fill", b.x, b.y, b.w, b.h)
        love.graphics.setColor(1, 1, 1)
    end
    love.graphics.setColor(1, 1, 1)

    -- Draw health boosters
    for _, booster in ipairs(healthBoosters) do
        if not booster.collected then
            love.graphics.setColor(0.2, 1, 0.2, 1)
            love.graphics.circle("fill", booster.x, booster.y, booster.r)
            love.graphics.setColor(1, 1, 1)
            love.graphics.setLineWidth(3)
            -- Draw a white cross
            love.graphics.line(booster.x - 7, booster.y, booster.x + 7, booster.y)
            love.graphics.line(booster.x, booster.y - 7, booster.x, booster.y + 7)
            love.graphics.setLineWidth(1)
        end
    end

    -- Draw Combat UI (Health, Score, Objective etc.)
    love.graphics.setFont(uiFonts.large)
    if combatObjects.player then
        love.graphics.print("Health: " .. combatObjects.player.health .. "/" .. (combatObjects.player.stats.maxHealth or 100), 20, 20)
        if combatObjects.player.maxShield and combatObjects.player.maxShield > 0 then
            love.graphics.setColor(0.2, 0.7, 1)
            love.graphics.print("Shield: " .. math.floor(combatObjects.player.shield) .. "/" .. combatObjects.player.maxShield, 20, 60)
            love.graphics.setColor(1, 1, 1)
        end
        if playerStats.ship.weaponName then
            love.graphics.setColor(1, 1, 0.3)
            love.graphics.print("Weapon: " .. playerStats.ship.weaponName, 20, 100)
            love.graphics.setColor(1, 1, 1)
        end
        love.graphics.setColor(1, 1, 0.3)
        love.graphics.print("Score: " .. playerScore, 20, 160)
        love.graphics.setColor(1, 1, 1)
    else
        love.graphics.print("PLAYER DESTROYED", 20, 20)
    end
    love.graphics.printf("Enemies Remaining: " .. #combatObjects.enemies, 0, 20, love.graphics.getWidth(), "right")
    love.graphics.setFont(uiFonts.normal)

    -- Draw radio message box if message is active
    if radioMessage then
        love.graphics.setFont(uiFonts.large)
        local boxW, boxH = 900, 120
        local boxX = love.graphics.getWidth() - boxW - 32
        local boxY = BASE_HEIGHT - boxH - 32
        love.graphics.setColor(0.1, 0.15, 0.18, 0.92)
        love.graphics.rectangle("fill", boxX, boxY, boxW, boxH, 18, 18)
        love.graphics.setColor(0.2, 1, 0.2, 1)
        love.graphics.rectangle("line", boxX, boxY, boxW, boxH, 18, 18)
        love.graphics.setColor(0.2, 1, 0.2, 1)
        love.graphics.setFont(love.graphics.newFont(48))
        love.graphics.print("[RADIO]", boxX + 28, boxY + 24)
        love.graphics.setColor(1, 1, 1, 1)
        love.graphics.setFont(love.graphics.newFont(44))
        love.graphics.printf(radioMessage, boxX + 200, boxY + 24, boxW - 220, "left")
        love.graphics.setFont(uiFonts.normal)
    end
end

function handleCombatKeyInput(key, isPressed)
     if not combatObjects.player or isGameOver then return end -- No input if player is dead or game over

     local value = isPressed and 1 or 0

     if key == "w" or key == "up" then
         combatObjects.player.moveInput.y = -value
     elseif key == "s" or key == "down" then
         combatObjects.player.moveInput.y = value
     elseif key == "a" or key == "left" then
         combatObjects.player.moveInput.x = -value
     elseif key == "d" or key == "right" then
         combatObjects.player.moveInput.x = value
     elseif key == "kp8" then
         playerAim.x, playerAim.y = 0, -1
     elseif key == "kp2" then
         playerAim.x, playerAim.y = 0, 1
     elseif key == "kp4" then
         playerAim.x, playerAim.y = -1, 0
     elseif key == "kp6" then
         playerAim.x, playerAim.y = 1, 0
     elseif key == "kp7" then
         playerAim.x, playerAim.y = -1, -1
     elseif key == "kp9" then
         playerAim.x, playerAim.y = 1, -1
     elseif key == "kp1" then
         playerAim.x, playerAim.y = -1, 1
     elseif key == "kp3" then
         playerAim.x, playerAim.y = 1, 1
     elseif key == "space" then
         playerHoldingFire = isPressed
     elseif key == "q" then
         if isPressed then
             playerSpinning = true
             spinTimer = SPIN_DURATION
         end
     end

     -- Normalize diagonal movement
     if combatObjects.player.moveInput.x ~= 0 and combatObjects.player.moveInput.y ~= 0 then
         local len = math.sqrt(combatObjects.player.moveInput.x^2 + combatObjects.player.moveInput.y^2)
         combatObjects.player.moveInput.x = combatObjects.player.moveInput.x / len * value -- Re-apply value after normalizing
         combatObjects.player.moveInput.y = combatObjects.player.moveInput.y / len * value
     end
end

function handleCombatMouseInput(x, y, button)
    if button == 1 and combatObjects.player then -- Left click to shoot
        combatObjects.player:shoot(x / scaleX, y / scaleY) -- Adjust for scaling
    end
end

-- =========================================================================
-- HARVESTING STATE
-- =========================================================================
local harvestedPlanet = nil
local harvestTimer = 0
local timeToShowHarvest = 3 -- seconds

function initializeHarvestingState(planet)
    print("Initializing Harvesting State for:", planet.name)
    harvestedPlanet = planet
    harvestTimer = timeToShowHarvest

    -- Award Resources
    local resourceName = planet.resource
    local amountGained = math.random(5, 10) -- Example: random amount gained
    if playerResources[resourceName] then
        playerResources[resourceName] = playerResources[resourceName] + amountGained
    else
        playerResources[resourceName] = amountGained -- First time getting this resource
    end
    print("Harvested", amountGained, resourceName)

    -- Mark planet as conquered only if base is destroyed
    if planet.baseDestroyed then
        planet.conquered = true
    end
end

function updateHarvestingState(dt)
    harvestTimer = harvestTimer - dt
    if harvestTimer <= 0 then
        -- If all planets conquered, move to next galaxy (don't skip levels)
        if allPlanetsConquered() then
            generateNewGalaxy()
            -- Don't call initializeMapState again, just return to map for new galaxy
            changeState("map")
        else
            changeState("map") -- Go back to map after showing results
        end
    end
end

function drawHarvestingState()
    -- Draw semi-transparent overlay
    love.graphics.setColor(0, 0, 0, 0.7)
    love.graphics.rectangle("fill", 0, 0, love.graphics.getWidth(), love.graphics.getHeight())
    love.graphics.setColor(1, 1, 1, 1)

    -- Display harvest results
    love.graphics.setFont(uiFonts.large)
    local text = string.format("Victory on %s!\n\nHarvested %d %s!\n\nReturning to Galaxy Map...",
                                harvestedPlanet.name,
                                playerResources[harvestedPlanet.resource], -- Show total amount now
                                harvestedPlanet.resource)
    love.graphics.printf(text, 0, love.graphics.getHeight() / 2 - 50, love.graphics.getWidth(), "center")
    love.graphics.setFont(uiFonts.normal)
end

-- =========================================================================
-- TRAVELING STATE (Optional - Simple placeholder)
-- =========================================================================
local travelTimer = 0
local timeToTravel = 1.5 -- seconds

function initializeTravelingState(targetState, ...) -- e.g., initializeTravelingState("combat", planet)
    print("Initializing Traveling State")
    -- Store where to go next and with what arguments
    travelTimer = timeToTravel
    -- TODO: Store targetState and arguments
end

function updateTravelingState(dt)
     travelTimer = travelTimer - dt
    if travelTimer <= 0 then
        -- TODO: changeState(targetState, ...) -- Change to the actual destination state
        print("DEBUG: Travel finished, would normally go to combat/map now")
        -- For now, just skip back to map for simplicity in this example
        changeState("map")
    end
end

function drawTravelingState()
    love.graphics.setBackgroundColor(0, 0, 0)
    love.graphics.setColor(1, 1, 1)
    love.graphics.printf("Traveling...", 0, love.graphics.getHeight() / 2 - 10, love.graphics.getWidth(), "center")
    -- Could add star streaks or ship animations here
end