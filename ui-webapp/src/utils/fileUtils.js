export const blobToDataURL = async (blob) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (_e) => resolve(reader.result);
    reader.onerror = (_e) => reject(reader.error);
    reader.onabort = (_e) => reject(new Error("Read aborted"));
    reader.readAsDataURL(blob);
  });
};

const cleanB64 = (b64Str) => {
  return b64Str
    .replace(/^data:image\/(png|jpg|jpeg);base64,/, "")
    .replace("data:application/octet-stream;base64,", "");
};

export const downloadB64AsFile = (filename, data) => {
  data = cleanB64(data);
  var element = document.createElement("a");
  element.setAttribute("href", "data:text/plain;base64," + data);
  element.setAttribute("download", filename);
  element.style.display = "none";
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
};
