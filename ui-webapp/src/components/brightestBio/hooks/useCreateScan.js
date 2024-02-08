import { useState, useCallback, useEffect, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { getProducts } from '../../../actions/productActions';
import { saveScanWithWells } from '../../../actions/scanActions';
import { productSelector } from '../../../features/product/productSlice.js';
import { clearLastSavedScan, scanSelector } from '../../../features/scan/scanSlice';

export const useCreateScan = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  /**
   * name: string added by create scan flow
   * protocol: string added by scanActions->saveScanWithWells
   * productId: string added by create scan flow
   * protocolArgs: object added by scanActions->saveScanWithWells
   * readerSerialNumber: string added by create scan flow
   * selectedWells: array of objects added by create scan flow
   */
  const [scan, setScan] = useState(null);
  const [scanCreationInProgress, setScanCreationInProgress] = useState(false);
  const { lastSavedScan } = useSelector(scanSelector);
  const scanCreationFailed = useMemo(() => !!lastSavedScan?.error, [lastSavedScan]);

  const toViewScans = useCallback((id) => {
    navigate(`/scan/view-all?scan=${id}`, { replace: true });
  }, [navigate, lastSavedScan]);

  const saveScan = useCallback(async () => {
    setScanCreationInProgress(true);
    dispatch(saveScanWithWells(scan))
    console.debug('scan', scan);
  }, [scan]);

  useEffect(() => {
    if (lastSavedScan?._id && scanCreationInProgress) {
      setScanCreationInProgress(false);
      dispatch(clearLastSavedScan());
      toViewScans(lastSavedScan?._id);
    } else if (lastSavedScan?.error && scanCreationInProgress) {
      setScanCreationInProgress(false);
    }
  }, [lastSavedScan]);

  return { scan, setScan, saveScan, scanCreationInProgress, scanCreationFailed };
}
