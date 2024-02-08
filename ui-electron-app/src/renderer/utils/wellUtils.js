
const generateBlankPlate = () => {
    const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
    const columns = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    return Array.from({ length: 96 }, (v, i) => ({
        label: '',
        row: rows[Math.floor(i / 12)],
        column: columns[i % 12].toString(),
        type: 'empty',
    }));

}

export const getWellsFromScan = (scan) => {
    const wells = generateBlankPlate();
    const scanSelectedWells = scan?.protocolArgs?.images;
    return wells?.map(well => { 
        const selectedWell = scanSelectedWells?.find(scanSelectedWell => scanSelectedWell.name === `${well.row}${well.column}`);
        return { ...well, type: selectedWell ? 'selected' : 'empty' };
    })
}

export const getWellsFromAnalysis = (analysis) => analysis?.protocolArgs?.wells || generateBlankPlate();
