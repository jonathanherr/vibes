-- cards.lua
local Cards = {}

Cards.deck = {
    -- Ship Cards (determine the type of invaders spawned)
    { name = "Basic Invader", type = "ship", effect = { type = "basic", count = 20 }, description = "A standard, numerous invader." },
    { name = "Fast Invader", type = "ship", effect = { type = "fast", count = 15 }, description = "Moves and shoots faster." },
    { name = "Tank Invader", type = "ship", effect = { type = "tank", count = 10 }, description = "Slow but has more health." },
    { name = "Swarmers", type = "ship", effect = { type = "basic", count = 30 }, description = "Deploys more basic invaders." }, -- Example of tuning count
    { name = "Marauders", type = "ship", effect = { type = "fast", count = 20 }, description = "Deploys more fast invaders." },

    -- Powerup Cards (global modifiers for the battle)
    { name = "Invader Speed Boost", type = "powerup", effect = { modifier = "invaderSpeed", value = 1.5 }, description = "All invaders move 50% faster." },
    { name = "Invader Rapid Fire", type = "powerup", effect = { modifier = "invaderFireRate", value = 0.7 }, description = "Invaders shoot 30% more often (lower delay)." }, -- Value is a multiplier for delay
    { name = "Invader Toughness", type = "powerup", effect = { modifier = "invaderHealth", value = 1.5 }, description = "All invaders have 50% more health." },
    { name = "Shield Buster Shots", type = "powerup", effect = { modifier = "invaderShieldDamage", value = 2 }, description = "Invader shots do double damage to shields." },
    { name = "Defender Jammer", type = "powerup", effect = { modifier = "defenderFireRate", value = 1.5 }, description = "Defender shoots 50% less often (higher delay)." },
    { name = "Cannon Weakpoint", type = "powerup", effect = { modifier = "defenderHealth", value = 0.5 }, description = "Defender has 50% less health." },
}

-- Assign placeholder images (replace with actual loading later)
for i, card in ipairs(Cards.deck) do
    if card.effect.type == "basic" then
        card.image = Assets.invaderImg -- Need logic to pick image based on effect.type
    elseif card.effect.type == "fast" then
        card.image = Assets.fastInvaderImg
     elseif card.effect.type == "tank" then
        card.image = Assets.tankInvaderImg
    else -- Powerup cards might use the card back or a generic icon
         card.image = Assets.cardBackImg -- Placeholder
    end
end


-- Function to get a shuffled deck
function Cards.getShuffledDeck()
    local deckCopy = {}
    for i, card in ipairs(Cards.deck) do
        table.insert(deckCopy, card)
    end

    -- Fisher-Yates shuffle
    local n = #deckCopy
    while n > 1 do
        local k = math.random(n)
        deckCopy[n], deckCopy[k] = deckCopy[k], deckCopy[n]
        n = n - 1
    end
    return deckCopy
end

return Cards
