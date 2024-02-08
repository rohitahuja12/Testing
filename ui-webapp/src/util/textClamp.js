export function textClamp(itemText, maxLength) {
  const maxLengthOfLink = maxLength; // maximum no. of characters you want your text to have
  const itemTextArray = itemText.split(' ');
  let reducedFlag = -1;

  return itemTextArray.reduce((accumulator, currentVal) => {
    if (accumulator.length + currentVal.length > maxLengthOfLink) {
      // eslint-disable-next-line no-plusplus
      reducedFlag++;
      return reducedFlag ? accumulator : `${accumulator}...`;
    }
    return `${accumulator} ${currentVal}`;
  });
}
