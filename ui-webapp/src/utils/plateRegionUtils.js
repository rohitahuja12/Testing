/**
 * 
 * @param {[[], []]} plate 
 * @param {object} currentSelectedWell 
 * @returns {object} with coordinates of the selected well
 */
const getWellWithCoords = (plate, currentSelectedWell) => plate.reduce((acc, curr) => {
    const detailedWell = curr.find(well => (well.row === currentSelectedWell.row
        && well.column === currentSelectedWell.column));
    return detailedWell ? detailedWell : acc;
}, null);

const isWellAdjacentToWell = (well1, well2) => {
    const x1 = well1.x, y1 = well1.y, x2 = well2.x, y2 = well2.y;
    const isAdjacentX = (x1 === x2 || x1 === x2 + 1 || x1 === x2 - 1) && y1 === y2;
    const isAdjacentY = (y1 === y2 || y1 === y2 + 1 || y1 === y2 - 1) && x1 === x2;
    return isAdjacentX || isAdjacentY;
}

const isWellAdjacentToCollection = (collection, well) => collection.wells
    .some(collectionWell => isWellAdjacentToWell(well, collectionWell));

// collection + current well is a simple "rectangle" 
const isWellInlineWithCollection = (well, collection) => collection.wells
    .every(collectionWell => (well.x === collectionWell.x || well.y === collectionWell.y));

const collectionHasUnseenAdjacents = (collection, seenSelectedWells) => {
    const adjacents = seenSelectedWells.filter(well => isWellAdjacentToCollection(collection, well));
    return adjacents.some(well => !well.seen);
}

const showLogs = false;
const debugLog = showLogs ? console.log : () => { };

/**
 * 
 * @param {[], []} plate 
 * @param {[]} selectedWells 
 */
export const getRegionsBySelectedWells = (selectedWells) => {
    // https://auragentbioscience.slack.com/archives/C03H7B3ME4T/p1658415952892559
    return selectedWells.map(selectedWell => ({
        name: `${selectedWell.row}${selectedWell.column}`,
        region: [{
            feature: ["Well", selectedWell.row, selectedWell.column],
        }]
    }));
}

/**
 * 
 * @param {[[], []]} plate 
 * @param {[]} selectedWells 
 */
export const getPlateRegionsWithSelectedWells = (plate, selectedWells) => {
    let collections = []
        , bookmarks = [],
        seenSelectedWells = [];
    let loops = 0;

    debugLog('***************HERE WE GO**********************');
    debugLog('[Algo]: Collections size: ', collections.length);

    do {
        loops++;
        debugLog('[Algo]: Starting a loop of the algorithm');
        debugLog('[Algo]: bookmarks size: ', bookmarks.length);
        selectedWells = selectedWells ? [...selectedWells] : [];
        selectedWells = bookmarks?.length > 0
            ? selectedWells.filter(selectedWell => bookmarks.find(bookmark => bookmark.row === selectedWell.row && bookmark.column === selectedWell.column))
            : selectedWells;
        seenSelectedWells = [];
        bookmarks = [];


        selectedWells
            ?.sort((a, b) => {
                if (a.row === b.row) {
                    return a.column - b.column;
                }
                return (a.row > b.row) ? 1 : -1
            })
            ?.map((currentSelectedWell, currentIndex) => {
                const currentWell = getWellWithCoords(plate, currentSelectedWell);
                debugLog('[Algo]: currentWell...', currentWell);

                if (collections.length === 0
                    || collections.every(collection => collection.filled === true)) {
                    // new collection needed
                    debugLog('[Algo]: New collection necessary, adding current well...', currentWell);
                    collections = [...collections, {
                        wells: [currentWell],
                        filled: false
                    }];
                } else {
                    // get non-filled collection
                    const collection = collections.find(collection => collection.filled === false);
                    debugLog('[Algo]: There exists a non-filled collection...', collection.wells);

                    const detailedSelectedWells = selectedWells
                        .map(selectedWell => getWellWithCoords(plate, selectedWell))
                        .map(selectedWell => seenSelectedWells
                            .find(seenWell => seenWell.row === selectedWell.row && seenWell.column === selectedWell.column)
                            || selectedWell)

                    if (!collectionHasUnseenAdjacents(collection, detailedSelectedWells)) {
                        debugLog('[Algo]: Collection has no unseen adjacents...', collection.wells, detailedSelectedWells);
                        debugLog('[Algo]: Collection is filled...');
                        collection.filled = true;

                        // clear the seen property from bookmarked wells?
                    }

                    const isAdjacent = isWellAdjacentToCollection(collection, currentWell);
                    debugLog('[Algo]: Is current well adjacent to collection?', isAdjacent);

                    if (isAdjacent) {
                        // can we make a "simple" rectangle?
                        const isInline = isWellInlineWithCollection(currentWell, collection);
                        debugLog('[Algo]: Is current well inline with collection?', isInline);

                        if (isInline) {
                            debugLog('[Algo]: Current well is inline with collection...');
                            collection.wells = [...collection.wells, currentWell];
                        } else {
                            debugLog('[Algo]: Current well is not inline with collection, bookmarking current well...', currentWell);
                            // check if a rectangle could be formed with adjacent wells
                            bookmarks = [...bookmarks, currentWell];
                        }

                    } else {
                        // bookmark the current well
                        debugLog('[Algo]: Bookmarking the current well...', currentWell);
                        bookmarks = [...bookmarks, currentWell];
                    }

                    // is the current well adjacent to the collection? 
                    //    yes -> then a rectangle could be formed
                    //    no  -> bookmark the current well
                    // is the collection + current a rectangle? aka "simple"?
                    //    yes -> add current to collection
                    //    no  -> could a  rectangle be formed with adjacents?
                    //          yes -> get the wells adjacent to both 
                    //                 the current well and the collection
                    //                 which are not already in a collection
                    //                 AND are selected
                    //          no  -> bookmark the current well
                    // 

                    // Are there any more adjacent, selected wells to the collection?
                    //    yes ->  keep iterating
                    //    no  ->  mark the collection as filled


                }


                seenSelectedWells = [...seenSelectedWells, { ...currentWell, seen: true }];

                return { ...currentSelectedWell, seen: true };

            });

        // we went through all selected wells and found no fit for the
        // unfilled collection, so we need to create a new one in the 
        // next iteration (if there are bookmarks)

        collections = collections.map(collection => ({
            ...collection,
            filled: true
        }));

        debugLog('[Algo]: Collections size: ', collections.length);
        collections.forEach(debugLog);
        debugLog('[Algo]: Bookmarks: ', bookmarks);
        debugLog('[Algo]: Seen selected wells: ', seenSelectedWells);
        debugLog('loops: ', loops);

    } while (bookmarks.length > 0);

    const regions = collections.map(collection => ({
        region: collection.wells.map(well => ({
            feature: ["Well", well.row, well.column],
        })),
        laserOn: true
    }));

    return regions;
}
