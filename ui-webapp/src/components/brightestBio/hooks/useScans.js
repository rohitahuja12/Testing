import { useState, useCallback, useEffect, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { getScansWithoutWellData, saveScanWithWells } from '../../../actions/scanActions';
import { scanSelector } from '../../../features/scan/scanSlice';

// sample scan object
// {
//   "_id": "63600fc65ef215e24ff2ba8d",
//   "createdOn": "2022-10-31T18:11:18.812437",
//   "name": "Test PHX Scan",
//   "productId": "63600b855ef215e24ff2ba6d",
//   "protocol": "pArray",
//   "readerSerialNumber": "3",
//   "status": "COMPLETE"
// }
export const useScans = () => {
  const dispatch = useDispatch();
  const { scans, lastScanUpdate } = useSelector(scanSelector);

  useEffect(() => {
    if (dispatch) {
      dispatch(getScansWithoutWellData())
    }
  }, [dispatch, lastScanUpdate]);

  return { scans };
}
