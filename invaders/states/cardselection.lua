-- states/cardselection.lua
local CardSelectionState = {}

local Cards = require("cards") -- Load card data
local hand = {} -- The 5 cards drawn
local selected = {} -- The 3 cards the player has selected

local cardWidth = 120 * GameScale -- Increased from 100
local cardHeight = 180 * GameScale -- Increased from 150
local cardSpacing = 25 * GameScale -- Slightly increased spacing
local handY = 200 * GameScale
local deployButton = {x = 500 * GameScale, y = 400 * GameScale, width = 100 * GameScale, height = 40 * GameScale}

function CardSelectionState.enter()
    print("Entering Card Selection State")
    hand = {}
    selected = {}

    local deck = Cards.getShuffledDeck()

    -- Draw 5 cards (or fewer if deck runs out, though our deck is big enough)
    for i = 1, math.min(5, #deck) do
        table.insert(hand, table.remove(deck, 1))
    end
end

function CardSelectionState.update(dt)
    -- Handle hover effects (optional, but good UX)
end

function CardSelectionState.draw()
    love.graphics.setColor(1, 1, 1)
    love.graphics.setFont(Assets.font)

    love.graphics.printf("Choose 3 Cards to Deploy", 50 * GameScale, 50 * GameScale, love.graphics.getWidth(), "left")

    -- Draw hand cards
    local startX = (love.graphics.getWidth() - (#hand * cardWidth + (#hand - 1) * cardSpacing)) / 2
    for i, card in ipairs(hand) do
        local cardX = startX + (i - 1) * (cardWidth + cardSpacing)
        local cardY = handY

        -- Check if this card is selected
        local isSelected = false
        for j, s_card in ipairs(selected) do
            if s_card == card then
                isSelected = true
                break
            end
        end

        -- Draw card background/border
        if isSelected then
            love.graphics.setColor(0.8, 0.8, 1, 1) -- Highlight color
            love.graphics.rectangle("line", cardX - 2 * GameScale, cardY - 2 * GameScale, cardWidth + 4 * GameScale, cardHeight + 4 * GameScale)
            love.graphics.setColor(1, 1, 1)
        end

        -- Draw card (placeholder or image)
        -- Use placeholder rectangles for now
        love.graphics.setColor(0.5, 0.5, 0.5)
        love.graphics.rectangle("fill", cardX, cardY, cardWidth, cardHeight)
        love.graphics.setColor(1, 1, 1)
        love.graphics.rectangle("line", cardX, cardY, cardWidth, cardHeight)

        -- Draw card name and type
        love.graphics.printf(card.name, cardX + 5 * GameScale, cardY + 5 * GameScale, cardWidth - 10 * GameScale, "center")
        love.graphics.printf(card.type, cardX + 5 * GameScale, cardY + 25 * GameScale, cardWidth - 10 * GameScale, "center")
        love.graphics.printf(card.description, cardX + 5 * GameScale, cardY + 50 * GameScale, cardWidth - 10 * GameScale, "left")
         if card.image then -- Draw card image if available
             local imgScale = math.min(cardWidth / card.image:getWidth(), cardHeight / card.image:getHeight()) * 0.5 -- Scale down
             love.graphics.draw(card.image, cardX + cardWidth/2, cardY + cardHeight - (card.image:getHeight() * imgScale / 2) - (10 * GameScale), 0, imgScale, imgScale, card.image:getWidth()/2, card.image:getHeight()/2)
         end
    end

    -- Draw selected count
    love.graphics.printf("Selected: " .. #selected .. " / 3", 50 * GameScale, 400 * GameScale, love.graphics.getWidth(), "left")

    -- Draw Deploy button
    local buttonColor = (#selected == 3) and {0, 1, 0} or {0.5, 0.5, 0.5} -- Green if 3 selected, grey otherwise
    love.graphics.setColor(unpack(buttonColor))
    love.graphics.rectangle("fill", deployButton.x, deployButton.y, deployButton.width, deployButton.height)
    love.graphics.setColor(1, 1, 1)
    love.graphics.rectangle("line", deployButton.x, deployButton.y, deployButton.width, deployButton.height)
    love.graphics.printf("Deploy", deployButton.x, deployButton.y + (deployButton.height - Assets.font:getHeight() * GameScale)/2, deployButton.width, "center")
end

function CardSelectionState.mousepressed(x, y, button)
    if button == 1 then -- Left click
        -- Check card clicks
        local startX = (love.graphics.getWidth() - (#hand * cardWidth + (#hand - 1) * cardSpacing)) / 2
        for i, card in ipairs(hand) do
            local cardX = startX + (i - 1) * (cardWidth + cardSpacing)
            local cardY = handY

            if x > cardX and x < cardX + cardWidth and y > cardY and y < cardY + cardHeight then
                local isSelected = false
                local selectedIndex = -1
                for j, s_card in ipairs(selected) do
                    if s_card == card then
                        isSelected = true
                        selectedIndex = j
                        break
                    end
                end

                if isSelected then
                    -- Deselect card
                    table.remove(selected, selectedIndex)
                elseif #selected < 3 then
                    -- Select card
                    table.insert(selected, card)
                end
                return -- Click handled
            end
        end

        -- Check Deploy button click
        if #selected == 3 then
            if x > deployButton.x and x < deployButton.x + deployButton.width and y > deployButton.y and y < deployButton.y + deployButton.height then
                -- Transition to battle state, passing selected cards
                changeState("battle", { selectedCards = selected })
            end
        end
    end
end

function CardSelectionState.exit()
    print("Exiting Card Selection State")
    -- Clean up any state-specific resources if necessary
end

return CardSelectionState
