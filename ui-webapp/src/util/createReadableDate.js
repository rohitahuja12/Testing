
const getTime = (date) => {
  var hours = date.getHours();
  var minutes = date.getMinutes();
  var ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12; // the hour '0' should be '12'
  minutes = minutes < 10 ? '0'+minutes : minutes;
  var strTime = hours + ':' + minutes + ' ' + ampm;
  return strTime;
}

export const createReadableDate = (dateInput) => {
  const date = new Date(dateInput);
  // const [month, day, year] = [String(date.getMonth() + 1).padStart(2, '0'), String(date.getDate()).padStart(2, '0'), date.getFullYear()];
  // return `${month}-${day}-${year} ${getTime(date)}`;
  return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
};

