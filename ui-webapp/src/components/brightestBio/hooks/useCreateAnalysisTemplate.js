import { useState, useCallback, useEffect, useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import {
  getDefaultPlateMaps,
  saveAnalysisTemplate,
} from "../../../actions/analysisTemplateActions";
import { WellType } from "../../../enums/WellType";
import {
  analysisSelector,
  defaultPlateMapsSelector,
  lastSavedAnalysisTemplateSelector,
  reset,
} from "../../../features/analysis/analysisSlice";

const rows = ["A", "B", "C", "D", "E", "F", "G", "H"];
const columns = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
const emptyPlate = Array.from({ length: 96 }, (v, i) => ({
  label: `${rows[Math.floor(i / 12)]}${columns[i % 12]}`,
  row: rows[Math.floor(i / 12)],
  column: columns[i % 12].toString(),
  type: "empty",
  knownConcentration: 1000.0,
  replicateIndex: 0,
}));

const getWellTypeShorthand = (longType, overrideLabel) => {
  if (longType === WellType.STANDARD) return "stnd";
  if (longType === WellType.UNKNOWN) return "unk";
  if (overrideLabel && longType === WellType.BLANK) return overrideLabel;
  return "empty";
};

export const useCreateAnalysisTemplate = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const lastSavedAnalysisTemplate = useSelector(
    lastSavedAnalysisTemplateSelector
  );
  const analysisCreationFailed = useMemo(
    () => !!lastSavedAnalysisTemplate?.error,
    [lastSavedAnalysisTemplate]
  );
  const [template, setTemplate] = useState({
    wells: emptyPlate,
  });
  const [templateName, setTemplateName] = useState("");
  const plateMaps = useSelector(defaultPlateMapsSelector) || [];
  const [templateCreationInProgress, setTemplateCreationInProgress] =
    useState(false);
  const [renameUnknownsModalOpen, setRenameUnknownsModalOpen] = useState(false);
  const [selectedPlateMap, setSelectedPlateMap] = useState(null);
  const [originalConcentrations, setOriginalConcentrations] = useState(null);
  const [concentrations, setConcentrations] = useState(null);
  const [standardDilution, setStandardDilution] = useState(3.0);
  const [thresholdAlgorithm, setThresholdAlgorithm] =
    useState("mean-threshold"); // mean-threshold, circle-threshold
  const [skipStandardConcentrationStep, setSkipStandardConcentrationStep] =
    useState(true);

  /**
   * @param {Array<object>} wells
   */
  const shouldSkipStandardConcentrationStep = (wells) =>
    !wells.some((well) => well.type === WellType.STANDARD);

  useEffect(() => {
    if (plateMaps?.length === 0) {
      dispatch(getDefaultPlateMaps());
    }
  }, [dispatch, plateMaps]);

  // use selected plate map to find the plate map details
  // then use the plate map details to set the template
  useEffect(() => {
    if (selectedPlateMap) {
      const plateMap = plateMaps.find(
        (plateMap) => plateMap._id === selectedPlateMap
      );
      if (plateMap) {
        const { map } = plateMap;
        setTemplate({
          ...template,
          wells: map,
        });
        setSkipStandardConcentrationStep(
          shouldSkipStandardConcentrationStep(map) // phoen-35
        );
      }
    }
  }, [
    selectedPlateMap,
    setSkipStandardConcentrationStep,
    shouldSkipStandardConcentrationStep,
    plateMaps,
    template,
  ]);

  /** sample analysis object
      protocol: 'pArrayFluoro', // TODO: where should this come from?
      name: analysis.name,
      productId: product._id,
      productName: product?.productName,
      notes: analysis.notes,
      protocolArgs: {
          initialConcentrations: concentrations,
          standardDilutionFactor: standardDilution,
          wells: templatedWells,
          initialConcentrationUnits: 'pg/ml'
      }
   */
  const createTemplate = useCallback(async () => {
    setTemplateCreationInProgress(true);
    dispatch(
      saveAnalysisTemplate({
        name: templateName,
        protocol: "pArrayFluoro", // TODO: where should this come from?
        productId: template.productId,
        productName: template.productName,
        protocolArgs: {
          initialConcentrations: concentrations,
          standardDilutionFactor: standardDilution,
          wells: template.wells,
          initialConcentrationUnits: "pg/ml", // TODO: Get this from product
          signalIntensityAlgorithm: thresholdAlgorithm,
        },
      })
    );
  }, [
    template,
    dispatch,
    templateName,
    concentrations,
    standardDilution,
    saveAnalysisTemplate,
    setTemplateCreationInProgress,
  ]);

  const getPlateMaps = useCallback(() => {
    dispatch(getDefaultPlateMaps());
  }, [dispatch]);

  const setWellTypes = useCallback(
    (changes) => {
      const updatedWells = [...template.wells];
      changes.forEach((change) => {
        const rowNumberRepresentation =
          change.row.toLowerCase().charCodeAt(0) - 97;
        const index = rowNumberRepresentation * 12 + (change.column - 1);
        let wellOfInterest = updatedWells[index];
        updatedWells[index] = {
          ...wellOfInterest,
          type: change.type,
          replicateIndex: change.replicateIndecesCount + 1,
          label: `${getWellTypeShorthand(change?.type, change?.overrideLabel)}${
            isNaN(change?.index) ? "" : change?.index + 1
          }`,
        };
      });
      setTemplate({ ...template, wells: updatedWells });
      setSkipStandardConcentrationStep(
        shouldSkipStandardConcentrationStep(updatedWells) // phoen-35
      );
    },
    [
      template,
      setTemplate,
      setSkipStandardConcentrationStep,
      shouldSkipStandardConcentrationStep,
    ]
  );

  const setWellType = useCallback(
    (action) => {
      setWellTypes([action]);
    },
    [template]
  );

  const resetWells = useCallback(() => {
    setTemplate({
      ...template,
      wells: emptyPlate,
    });
    setSelectedPlateMap(null);
    setSkipStandardConcentrationStep(true); // phoen-35
  }, [
    template,
    setTemplate,
    setSelectedPlateMap,
    setSkipStandardConcentrationStep,
  ]);

  const resetTemplate = useCallback(() => {
    setTemplate({
      wells: emptyPlate,
    });
    setSelectedPlateMap(null);
    setRenameUnknownsModalOpen(false);
    setTemplateCreationInProgress(false);
    setSkipStandardConcentrationStep(true); // phoen-35
  }, []);

  const setWells = useCallback(
    /**
     * @param {Array<object>} wells
     */
    (wells) => {
      setTemplate({
        ...template,
        wells,
      });
      setSkipStandardConcentrationStep(
        shouldSkipStandardConcentrationStep(wells) // phoen-35
      );
    },
    [
      template,
      setSkipStandardConcentrationStep,
      shouldSkipStandardConcentrationStep,
    ]
  );

  useEffect(() => {
    if (lastSavedAnalysisTemplate?._id) {
      setTemplateCreationInProgress(false);
      dispatch(reset());
      navigate("/analysis-template/view-all", { replace: true });
    } else if (lastSavedAnalysisTemplate?.error) {
      setTemplateCreationInProgress(false);
    }
  }, [lastSavedAnalysisTemplate]);

  return {
    template,
    setTemplate,
    createTemplate,
    templateCreationInProgress,
    setWellType,
    resetWells,
    resetTemplate,
    setWells,
    setWellTypes,
    renameUnknownsModalOpen,
    setRenameUnknownsModalOpen,
    plateMaps,
    getPlateMaps,
    selectedPlateMap,
    setSelectedPlateMap,
    templateName,
    setTemplateName,
    concentrations,
    setConcentrations,
    standardDilution,
    setStandardDilution,
    originalConcentrations,
    setOriginalConcentrations,
    analysisCreationFailed,
    thresholdAlgorithm,
    setThresholdAlgorithm,
    skipStandardConcentrationStep,
  };
};
