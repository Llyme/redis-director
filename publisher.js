import { weightedDistribution } from './helpers.js';
import { Subscriber } from './subscriber.js';

/**
 * @typedef {Object} PublisherOptions
 * @property {import('ioredis').Redis} redis
 * @property {string} scoreKey
 * @property {string} queueKey
 */

/**
 * @typedef {Object} AddSubscriberOptions
 * @property {string} scoreMember
 * @property {import('./constants.js').Handler} handler
 * @property {number} defaultScore
 * @property {number} minScore
 * @property {number} maxScore
 */

export class Publisher {
    /**
     * @type {Object.<string, Subscriber>}
     */
    #subscribers;
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
    #queueKey;

    /**
     * 
     * @param {PublisherOptions} param0 
     */
    constructor({
        redis,
        scoreKey,
        queueKey
    }) {
        this.#subscribers = {};
        this.#redis = redis;
        this.#scoreKey = scoreKey;
        this.#queueKey = queueKey;
    }

    get redis() {
        return this.#redis;
    }

    get scoreKey() {
        return this.#scoreKey;
    }

    get queueKey() {
        return this.#queueKey;
    }

    async resetScores() {
        for (const subscriber of Object.values(this.#subscribers))
            await subscriber.resetScore();
    }

    /**
     * 
     * @param {AddSubscriberOptions} param0 
     */
    addSubscriber({
        scoreMember,
        handler,
        defaultScore = 100,
        minScore = 1,
        maxScore = 100
    }) {
        return this.addSubscribers(
            new Subscriber({
                redis: this.#redis,
                scoreKey: this.scoreKey,
                scoreMember,
                defaultScore,
                minScore,
                maxScore,
                handler
            })
        );
    }

    /**
     * 
     * @param  {...Subscriber} subscribers 
     */
    addSubscribers(...subscribers) {
        for (const subscriber of subscribers)
            this.#subscribers[subscriber.scoreMember] = subscriber;

        return this;
    }

    /**
     * 
     * @param {number} batchSize 
     */
    async publish(batchSize = 1) {
        const payloads = await this.#redis.spop(
            this.#queueKey,
            batchSize
        );

        for (const payload of payloads) {
            const subscribers = weightedDistribution(
                Object.values(this.#subscribers),
                async subscriber => await subscriber.getScore()
            );

            for await (const subscriber of subscribers) {
                if (subscriber.handler != null)
                    await subscriber.handler(subscriber, payload);

                break;
            }
        }

        return this;
    }
}