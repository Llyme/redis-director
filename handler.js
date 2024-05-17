/**
 * 
 * @param {string} key 
 * @param {number} addScore 
 * @returns 
 */
export function genericSetHandler(key, addScore = -1) {
    /**
     * @type {import('./constants').Handler}
     */
    async function handler(subscriber, payload) {
        await subscriber.addScore(addScore);
        await subscriber.redis.sadd(key, payload);
    }

    return handler;
}

/**
 * 
 * @param {string} key 
 * @param {number} addScore 
 * @returns 
 */
export function genericListHandler(key, addScore = -1) {
    /**
     * @type {import('./constants').Handler}
     */
    async function handler(subscriber, payload) {
        await subscriber.addScore(addScore);
        await subscriber.redis.lpush(key, payload);
    }

    return handler;
}