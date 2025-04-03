-- conf.lua
function love.conf(t)
    t.window.width = 800
    t.window.height = 600
    t.window.title = "LÖVE 2D Boat Racer"
    t.modules.joystick = false -- Disable modules we don't need
    t.modules.physics = false
end