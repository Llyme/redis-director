INCREMENT_LUA_SCRIPT = """
local key = KEYS[1]
local member = ARGV[1]
local increment = tonumber(ARGV[2])
local minScore = tonumber(ARGV[4])
local maxScore = tonumber(ARGV[5])

local currentScore = redis.call('zscore', key, member)

if not currentScore then
    currentScore = tonumber(ARGV[3])
else
    currentScore = tonumber(currentScore)
end

local newScore = currentScore + increment

if newScore < minScore then
    newScore = minScore

elseif newScore > maxScore then
    newScore = maxScore

end

redis.call('zadd', key, newScore, member)

return newScore
"""
