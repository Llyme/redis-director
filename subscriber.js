import { INCREMENT_LUA_SCRIPT } from './constants.js';
import { v4 } from 'uuid';

/**
 * @typedef {Object} SubscriberOptions
 * @property {import('ioredis').Redis} redis
 * @property {string} scoreKey
 * @property {string} scoreMember
 * @property {number} defaultScore
 * @property {number} minScore
 * @property {number} maxScore
 * @property {import('./constants.js').Handler} handler
 */

export class Subscriber {
    /**
     * @type {import('ioredis').Redis}
     */
    #redis;
    /**
     * @type {string}
     */
    #scoreKey;
    /**
     * @type {string}
     */
    #scoreMember;
    /**
     * @type {number}
     */
    #defaultScore;
    /**
     * @type {number}
     */
    #minScore;
    /**
     * @type {number}
     */
    #maxScore;
    /**
     * @type {import('./constants.js').Handler}
     */
    #handler;
    #incrementGUID;

    /**
     * 
     * @param {SubscriberOptions} param0 
     */
    constructor({
        redis,
        scoreKey,
        scoreMember,
        defaultScore = 100,
        minScore = 1,
        maxScore = 100,
        handler = null,
    }) {
        this.#redis = redis;
        this.#scoreKey = scoreKey;
        this.#scoreMember = scoreMember;
        this.#defaultScore = defaultScore;
        this.#minScore = minScore;
        this.#maxScore = maxScore;
        this.#handler = handler;
        this.#incrementGUID = v4();

        redis.defineCommand(this.#incrementGUID, {
            lua: INCREMENT_LUA_SCRIPT,
            numberOfKeys: 1,
            readOnly: true
        });
    }

    get redis() {
        return this.#redis;
    }

    get scoreKey() {
        return this.#scoreKey;
    }

    get scoreMember() {
        return this.#scoreMember;
    }

    get defaultScore() {
        return this.#defaultScore;
    }

    get minScore() {
        return this.#minScore;
    }

    get maxScore() {
        return this.#maxScore;
    }

    get handler() {
        return this.#handler;
    }

    async getScore() {
        const score = await this.#redis.zscore(
            this.#scoreKey,
            this.#scoreMember
        );

        if (score === null)
            return this.#defaultScore;

        return parseFloat(score);
    }

    /**
     * 
     * @param {number} value 
     */
    async addScore(value) {
        return this.#redis[this.#incrementGUID](
            this.#scoreKey,
            this.#scoreMember,
            value,
            this.#defaultScore,
            this.#minScore,
            this.#maxScore
        );
    }

    /**
     * 
     * @param {number} value 
     */
    async setScore(value) {
        await this.#redis.zadd(
            this.#scoreKey,
            'NX',
            value,
            this.#scoreMember
        );

        return value;
    }

    async resetScore() {
        await this.setScore(this.#defaultScore);

        return this.#defaultScore;
    }
}
