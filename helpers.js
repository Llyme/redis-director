/**
 * @template T
 * @param {Iterable<T>} items 
 * @param {function(T): Promise<number>} weightSelector 
 */
export async function* weightedDistribution(items, weightSelector) {
    const weightedItems = [];

    for (const item of items) {
        const weight = await weightSelector(item);

        if (weight <= 0)
            continue;

        weightedItems.push({
            item,
            weight
        });
    }

    weightedItems.sort((a, b) => a.weight - b.weight);

    const maxWeight = weightedItems.reduce(
        (a, b) => a + b.weight,
        0
    );

    while (weightedItems.length > 0) {
        let value = Math.random() * maxWeight;

        for (const { item, weight } of weightedItems) {
            if (value < weight) {
                yield item;
                break;
            }

            value -= weight;
        }
    }
}