"""
OCAI Toolbox - High-Performance Compositional Data Analysis (CoDa) Engine
for the Organizational Culture Assessment Instrument (Cameron & Quinn).

Supports:
- Multiplicative zero replacement on simplex (base 100).
- Closed geometric mean on the simplex for CFP and CDP.
- Simplex block bootstrap with Aitchison confidence regions.
- Paired dimension-level permutation tests (Now vs. Preferred).
- Hierarchical sub-group / department analysis with homonymous sub-departments.
- Configurable minGroupSize filtering.
- Individualized department exports (Excel multi-sheet, CSV, JSON).
- Pure structured reports (OcaiSummaryReport) with rich HTML rendering for Jupyter.
- Competing Values Framework (CVF) radar charts.
"""

from __future__ import annotations
import math
import os
import json
from typing import Sequence, Any
import numpy as np
import polars as pl
import matplotlib.pyplot as plt


def closure(mat: np.ndarray, axis: int = -1) -> np.ndarray:
    """Perform closure operation on compositions so each row sums to 1."""
    arr = np.array(mat, dtype=float, copy=True)
    if not np.issubdtype(arr.dtype, np.number):
        raise TypeError("Input matrix must have a numeric data type.")
    if not np.all(np.isfinite(arr)):
        raise ValueError("Input matrix cannot have infinite or NaN values.")
    if np.any(arr < 0):
        raise ValueError("Input matrix cannot have negative components.")
    if np.any(~np.any(arr > 0, axis=axis)):
        raise ValueError("Input matrix cannot have compositions without observed components.")
    return arr / np.sum(arr, axis=axis, keepdims=True)


def multiReplace(mat: np.ndarray, delta: float | None = None) -> np.ndarray:
    """Multiplicative replacement strategy for zero values in compositions."""
    matClosed = closure(mat)
    zMat = (matClosed == 0)
    numFeats = matClosed.shape[-1]
    tot = zMat.sum(axis=-1, keepdims=True)

    if delta is None:
        delta = (1.0 / numFeats) ** 2

    zcnts = 1.0 - tot * delta
    if (zcnts < 0).any():
        raise ValueError("Multiplicative replacement created negative proportions. Consider using a smaller `delta`.")

    res = np.where(zMat, delta, zcnts * matClosed)
    return res.squeeze()


class OcaiGroupResult:
    """Container holding analytical and statistical results for a single group or overall."""

    def __init__(self, label: str, sampleSize: int):
        self.label = label
        self.sampleSize = sampleSize
        self.origValues: dict[str, float] = {}
        self.origDimValues: dict[str, float] = {}
        self.dfIntervalsCfp: pl.DataFrame | None = None
        self.dfIntervalsCdp: pl.DataFrame | None = None
        self.origDist: float = 0.0
        self.origDistDim: dict[str, float] = {}
        self.pValueGlobal: float = 1.0
        self.dfPermutationResults: pl.DataFrame | None = None


class OcaiSummaryReport:
    """Structured report holding all summary data for programmatic access and API serialization.

    Designed for AWS Lambda, REST APIs, microservices, and rich interactive Jupyter display.
    """

    def __init__(
        self,
        sampleSize: int,
        globalCfp: pl.DataFrame,
        globalHypothesisTest: dict[str, Any],
        dimensionalCdp: pl.DataFrame,
        benchmarking: pl.DataFrame | None = None,
        skippedGroups: list[dict[str, Any]] | None = None,
    ):
        self.sampleSize = sampleSize
        self.globalCfp = globalCfp
        self.globalHypothesisTest = globalHypothesisTest
        self.dimensionalCdp = dimensionalCdp
        self.benchmarking = benchmarking
        self.skippedGroups = skippedGroups or []

    def to_dict(self) -> dict[str, Any]:
        """Convert all metrics into a clean, JSON-serializable dictionary for AWS Lambda or REST APIs."""
        return {
            "sampleSize": self.sampleSize,
            "globalCfp": self.globalCfp.to_dicts(),
            "globalHypothesisTest": self.globalHypothesisTest,
            "dimensionalCdp": self.dimensionalCdp.to_dicts(),
            "benchmarking": self.benchmarking.to_dicts() if self.benchmarking is not None else None,
            "skippedGroups": self.skippedGroups,
        }

    def __str__(self) -> str:
        """Formatted plain-text representation for terminal or logs without hardcoded prints."""
        lines = [
            "=" * 80,
            f"OCAI ANALYSIS SUMMARY (Total Respondents: {self.sampleSize})",
            "=" * 80,
            "\n--- 1. OVERALL COLLECTIVE FULL PROFILE (CFP) & 95% CONFIDENCE INTERVALS ---",
            str(self.globalCfp),
            "\n--- 2. OVERALL HYPOTHESIS TEST (Now vs. Preferred) ---",
            f"Observed Aitchison Distance: {self.globalHypothesisTest['observedDistance']:.4f}",
            f"Empirical p-value:           {self.globalHypothesisTest['pValue']:.5f} (alpha = {self.globalHypothesisTest['alpha']})",
            f"Statistical Decision:        {self.globalHypothesisTest['decision']}",
            "\n--- 3. OVERALL DIMENSIONAL PROFILES (CDP) HYPOTHESIS TESTING ---",
            str(self.dimensionalCdp),
        ]

        if self.benchmarking is not None:
            lines.extend([
                "\n" + "=" * 80,
                "--- 4. SUB-GROUP / DEPARTMENT BENCHMARKING SUMMARY ---",
                "=" * 80,
                str(self.benchmarking),
            ])

        if self.skippedGroups:
            lines.append(f"\n[Note] Skipped {len(self.skippedGroups)} group(s) with size < minGroupSize:")
            for item in self.skippedGroups:
                lines.append(f"  - '{item['group']}': {item['respondents']} respondent(s)")

        return "\n".join(lines)

    def _repr_html_(self) -> str:
        """HTML representation for rich rendering in Jupyter Notebooks."""
        tableStyle = (
            "border-collapse: collapse; width: 100%; margin: 12px 0 20px 0; font-size: 0.9em; "
            "box-shadow: 0 0 10px rgba(0,0,0,0.05); border-radius: 6px; overflow: hidden;"
        )

        html = [
            f"<div style='font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #2c3e50;'>"
            f"<div style='background: linear-gradient(135deg, #1f77b4, #2ca02c); padding: 16px 20px; border-radius: 8px; color: white; margin-bottom: 20px;'>"
            f"<h2 style='margin: 0; font-size: 1.4em;'>OCAI Analysis Executive Report</h2>"
            f"<p style='margin: 4px 0 0 0; opacity: 0.9;'>Total Valid Respondents: <b>{self.sampleSize}</b></p>"
            f"</div>"

            f"<h3 style='color: #1f77b4; border-bottom: 2px solid #ecf0f1; padding-bottom: 6px;'>1. Global Collective Full Profile (CFP) & 95% Confidence Intervals</h3>",
            self._dataframeToHtml(self.globalCfp, tableStyle),

            f"<h3 style='color: #1f77b4; border-bottom: 2px solid #ecf0f1; padding-bottom: 6px;'>2. Global Hypothesis Test (Current vs. Preferred)</h3>"
            f"<div style='background-color: #f8f9fa; border-left: 4px solid {'#d62728' if self.globalHypothesisTest['pValue'] <= self.globalHypothesisTest['alpha'] else '#2ca02c'}; padding: 12px 16px; border-radius: 4px; margin: 12px 0;'>"
            f"<span style='font-size: 1.05em;'>Observed Aitchison Distance: <b>{self.globalHypothesisTest['observedDistance']:.4f}</b></span><br>"
            f"<span style='font-size: 1.05em;'>Empirical p-value: <b>{self.globalHypothesisTest['pValue']:.5f}</b> (significance level α = {self.globalHypothesisTest['alpha']})</span><br>"
            f"<span style='font-size: 1.1em; font-weight: bold;'>Decision: <span style='color: {'#d62728' if self.globalHypothesisTest['pValue'] <= self.globalHypothesisTest['alpha'] else '#2ca02c'};'>{self.globalHypothesisTest['decision']}</span></span>"
            f"</div>",

            f"<h3 style='color: #1f77b4; border-bottom: 2px solid #ecf0f1; padding-bottom: 6px;'>3. Dimensional Hypothesis Testing (CDP)</h3>",
            self._dataframeToHtml(self.dimensionalCdp, tableStyle),
        ]

        if self.benchmarking is not None:
            html.extend([
                f"<h3 style='color: #1f77b4; border-bottom: 2px solid #ecf0f1; padding-bottom: 6px;'>4. Sub-Group / Department Benchmarking Summary</h3>",
                self._dataframeToHtml(self.benchmarking, tableStyle),
            ])

        if self.skippedGroups:
            html.append("<p style='color: #7f8c8d; font-size: 0.9em; margin-top: 15px;'><b>Skipped sub-groups (size &lt; minGroupSize):</b><br>")
            for item in self.skippedGroups:
                html.append(f"• <i>{item['group']}</i> ({item['respondents']} respondents)<br>")
            html.append("</p>")

        html.append("</div>")
        return "".join(html)

    @staticmethod
    def _dataframeToHtml(df: pl.DataFrame, tableStyle: str) -> str:
        """Helper to render a Polars DataFrame into styled HTML table."""
        headers = [f"<th style='background-color: #f1f3f5; padding: 10px 14px; text-align: left; font-weight: 600; border-bottom: 2px solid #dee2e6;'>{col}</th>" for col in df.columns]
        headerRow = f"<tr>{''.join(headers)}</tr>"

        rows = []
        for i, row in enumerate(df.iter_rows()):
            bg = "#ffffff" if i % 2 == 0 else "#f8f9fa"
            cells = [f"<td style='padding: 8px 14px; border-bottom: 1px solid #dee2e6;'>{val}</td>" for val in row]
            rows.append(f"<tr style='background-color: {bg};'>{''.join(cells)}</tr>")

        return f"<table style='{tableStyle}'><thead>{headerRow}</thead><tbody>{''.join(rows)}</tbody></table>"


class OcaiAnalyzer:
    """High-performance analyzer for OCAI data with hierarchical sub-group support."""

    def __init__(
        self,
        filePath: str,
        separator: str = ";",
        groupBy: str | Sequence[str] | None = None,
        minGroupSize: int = 5,
        numSamples: int = 10000,
        numPermut: int = 5000,
        alpha: float = 0.05,
    ):
        self.filePath = filePath
        self.separator = separator
        self.minGroupSize = minGroupSize
        self.numSamples = numSamples
        self.numPermut = numPermut
        self.alpha = alpha

        # Parse groupBy hierarchy
        if groupBy is None:
            self.groupByCols: list[str] = []
        elif isinstance(groupBy, str):
            self.groupByCols = [groupBy]
        else:
            self.groupByCols = list(groupBy)

        # Domain structure
        self.colNameLevel1 = ["N", "P"]                      # Now, Preferred
        self.colNameLevel2 = ["1", "2", "3", "4", "5", "6"]  # 6 OCAI Dimensions
        self.colNameLevel3 = ["A", "B", "C", "D"]            # 4 Culture Types

        self.cultureNames = {
            "A": "Clan",
            "B": "Adhocracy",
            "C": "Market",
            "D": "Hierarchy",
        }

        self.dimensionNames = {
            "1": "1. Dominant Characteristics",
            "2": "2. Organizational Leadership",
            "3": "3. Management of Employees",
            "4": "4. Organization Glue",
            "5": "5. Strategic Emphases",
            "6": "6. Criteria of Success",
        }

        self.allColumns = [
            f"{l1}-{l2}-{l3}"
            for l1 in self.colNameLevel1
            for l2 in self.colNameLevel2
            for l3 in self.colNameLevel3
        ]

        self.colsDict = {
            f"{l1}-{l3}": [f"{l1}-{l2}-{l3}" for l2 in self.colNameLevel2]
            for l1 in self.colNameLevel1
            for l3 in self.colNameLevel3
        }

        self.revColsDict = {
            col: groupName
            for groupName, columns in self.colsDict.items()
            for col in columns
        }

        self.colsN = ["N-A", "N-B", "N-C", "N-D"]
        self.colsP = ["P-A", "P-B", "P-C", "P-D"]

        # Results containers
        self.dfRaw: pl.DataFrame | None = None
        self.dfPreprocessed: pl.DataFrame | None = None
        self.overallResult: OcaiGroupResult | None = None
        self.groupResults: dict[str, OcaiGroupResult] = {}
        self.skippedGroups: list[tuple[str, int]] = []

    def _calcMeans(self, dfInput: pl.DataFrame, meanTypes: dict, groupBy: str) -> pl.DataFrame:
        """Helper to calculate means aggregating columns with unpivot."""
        return (
            dfInput.unpivot(on=self.allColumns)
            .with_columns(pl.col("variable").replace(self.revColsDict).alias("group"))
            .group_by(groupBy)
            .agg(**meanTypes)
            .with_columns(pl.exclude(groupBy))
            .sort(groupBy)
        )

    @staticmethod
    def _aitchisonExpr(cols: list[str], valDict: dict[str, float], alias: str) -> pl.Expr:
        """Returns vectorized Polars expression for Aitchison distance against valDict."""
        logOrig = {c: math.log(valDict[c]) for c in cols}
        meanLogOrig = sum(logOrig.values()) / len(cols)
        clrOrig = {c: logOrig[c] - meanLogOrig for c in cols}

        meanLogSamples = pl.mean_horizontal([pl.col(c).log() for c in cols])
        diffQuadrados = [
            (pl.col(c).log() - meanLogSamples - clrOrig[c]) ** 2
            for c in cols
        ]
        return pl.sum_horizontal(diffQuadrados).sqrt().alias(alias)

    def loadAndPreprocess(self) -> None:
        """Load CSV data and perform per-dimension multiplicative zero replacement."""
        df = pl.read_csv(source=self.filePath, separator=self.separator)
        self.dfRaw = df.clone()

        missingCols = [c for c in self.allColumns if c not in df.columns]
        if missingCols:
            raise ValueError(f"Input CSV is missing required OCAI columns: {missingCols[:5]}...")

        if self.groupByCols:
            for c in self.groupByCols:
                if c not in df.columns:
                    raise ValueError(f"Specified grouping column '{c}' not found in CSV.")
            df = df.with_columns(
                pl.concat_str(self.groupByCols, separator=" > ").alias("groupLabel")
            )

        for l1 in self.colNameLevel1:
            for l2 in self.colNameLevel2:
                cols = [f"{l1}-{l2}-{l3}" for l3 in self.colNameLevel3]
                replaced = multiReplace(df.select(cols).to_numpy()) * 100.0
                df = df.with_columns(pl.DataFrame(replaced, schema=cols))

        self.dfPreprocessed = df

    def _processSubGroup(self, dfGroup: pl.DataFrame, label: str) -> OcaiGroupResult:
        """Run the complete bootstrap and permutation pipeline for a single group or overall."""
        groupRes = OcaiGroupResult(label=label, sampleSize=dfGroup.height)

        # 1. Baseline geometric means
        geomMean = {"geometric_mean": pl.col("value").log().mean().exp()}
        dimMeans = self._calcMeans(dfGroup, geomMean, "variable")
        means = self._calcMeans(dfGroup, geomMean, "group")

        groupRes.origDimValues = dict(dimMeans.iter_rows())
        groupRes.origValues = dict(means.iter_rows())

        # 2. Bootstrap
        originalDfSize = dfGroup.height
        total = self.numSamples * originalDfSize

        exprs = [
            pl.struct([f"{l1}-{l2}-{l3}" for l3 in self.colNameLevel3])
            .sample(n=total, with_replacement=True)
            .struct.unnest()
            for l1 in self.colNameLevel1
            for l2 in self.colNameLevel2
        ]

        dfSamples = (
            dfGroup.select(exprs)
            .with_columns((pl.int_range(0, total) // originalDfSize).alias("sampleId"))
        )

        logMeans = dfSamples.group_by("sampleId").agg(
            pl.all().exclude("sampleId").log().mean()
        )

        # CFP (Closed to 100)
        exprsGeom = [
            pl.mean_horizontal(cols).exp().alias(grp)
            for grp, cols in self.colsDict.items()
        ]
        sampleGeom = logMeans.select(["sampleId", *exprsGeom]).sort("sampleId")

        for l1 in self.colNameLevel1:
            cols = [f"{l1}-{l3}" for l3 in self.colNameLevel3]
            sumState = pl.sum_horizontal(cols)
            sampleGeom = sampleGeom.with_columns(
                [(pl.col(c) / sumState * 100.0).alias(c) for c in cols]
            )

        # CDP (Closed to 100)
        sampleGeomDim = logMeans.select(
            ["sampleId", *[pl.col(c).exp() for c in self.allColumns]]
        ).sort("sampleId")

        for l1 in self.colNameLevel1:
            for l2 in self.colNameLevel2:
                cols = [f"{l1}-{l2}-{l3}" for l3 in self.colNameLevel3]
                sumDim = pl.sum_horizontal(cols)
                sampleGeomDim = sampleGeomDim.with_columns(
                    [(pl.col(c) / sumDim * 100.0).alias(c) for c in cols]
                )

        # Aitchison Distances
        dfDistancias = sampleGeom.with_columns(
            self._aitchisonExpr(self.colsN, groupRes.origValues, alias="distN"),
            self._aitchisonExpr(self.colsP, groupRes.origValues, alias="distP"),
        )

        distDimExprs = []
        for d in self.colNameLevel2:
            colsDimN = [f"N-{d}-{c}" for c in self.colNameLevel3]
            colsDimP = [f"P-{d}-{c}" for c in self.colNameLevel3]
            distDimExprs.append(self._aitchisonExpr(colsDimN, groupRes.origDimValues, alias=f"distN_{d}"))
            distDimExprs.append(self._aitchisonExpr(colsDimP, groupRes.origDimValues, alias=f"distP_{d}"))

        dfDistanciasDim = sampleGeomDim.with_columns(distDimExprs)

        # Confidence Intervals
        condN = pl.col("distN") <= pl.col("distN").quantile(1.0 - self.alpha)
        condP = pl.col("distP") <= pl.col("distP").quantile(1.0 - self.alpha)

        groupRes.dfIntervalsCfp = dfDistancias.select([
            *[pl.col(c).filter(condN).min().alias(f"{c}_min") for c in self.colsN],
            *[pl.col(c).filter(condN).max().alias(f"{c}_max") for c in self.colsN],
            *[pl.col(c).filter(condP).min().alias(f"{c}_min") for c in self.colsP],
            *[pl.col(c).filter(condP).max().alias(f"{c}_max") for c in self.colsP],
        ])

        ciDimExprs = []
        for d in self.colNameLevel2:
            condDimN = pl.col(f"distN_{d}") <= pl.col(f"distN_{d}").quantile(1.0 - self.alpha)
            condDimP = pl.col(f"distP_{d}") <= pl.col(f"distP_{d}").quantile(1.0 - self.alpha)
            for c in self.colNameLevel3:
                colN = f"N-{d}-{c}"
                colP = f"P-{d}-{c}"
                ciDimExprs.extend([
                    pl.col(colN).filter(condDimN).min().alias(f"{colN}_min"),
                    pl.col(colN).filter(condDimN).max().alias(f"{colN}_max"),
                    pl.col(colP).filter(condDimP).min().alias(f"{colP}_min"),
                    pl.col(colP).filter(condDimP).max().alias(f"{colP}_max"),
                ])

        groupRes.dfIntervalsCdp = dfDistanciasDim.select(ciDimExprs)

        # 3. Permutation Test
        totalRows = self.numPermut * dfGroup.height
        dfRepeated = pl.concat([dfGroup] * self.numPermut).with_columns(
            (pl.int_range(0, totalRows) // dfGroup.height).alias("sampleId")
        )

        swapExprs = []
        for l2 in self.colNameLevel2:
            swap = pl.select(
                pl.int_range(0, totalRows).sample(fraction=1.0, shuffle=True) % 2 == 0
            ).to_series()

            for l3 in self.colNameLevel3:
                colN = f"N-{l2}-{l3}"
                colP = f"P-{l2}-{l3}"
                swapExprs.append(pl.when(swap).then(pl.col(colP)).otherwise(pl.col(colN)).alias(colN))
                swapExprs.append(pl.when(swap).then(pl.col(colN)).otherwise(pl.col(colP)).alias(colP))

        dfPermut = dfRepeated.with_columns(swapExprs)
        logMeansPerm = dfPermut.group_by("sampleId").agg(pl.all().exclude("sampleId").log().mean())

        exprsGeomPerm = [
            pl.mean_horizontal(cols).exp().alias(grp)
            for grp, cols in self.colsDict.items()
        ]
        permutGeom = logMeansPerm.select(["sampleId", *exprsGeomPerm]).sort("sampleId")

        meanLogN = pl.mean_horizontal([pl.col(f"N-{c}").log() for c in self.colNameLevel3])
        meanLogP = pl.mean_horizontal([pl.col(f"P-{c}").log() for c in self.colNameLevel3])
        diffQuadradosPerm = [
            ((pl.col(f"N-{c}").log() - meanLogN) - (pl.col(f"P-{c}").log() - meanLogP)) ** 2
            for c in self.colNameLevel3
        ]
        dfDistPermut = permutGeom.select(
            pl.col("sampleId"),
            pl.sum_horizontal(diffQuadradosPerm).sqrt().alias("distPermut"),
        )

        distDimPermExprs = []
        for d in self.colNameLevel2:
            meanLogDimN = pl.mean_horizontal([pl.col(f"N-{d}-{c}") for c in self.colNameLevel3])
            meanLogDimP = pl.mean_horizontal([pl.col(f"P-{d}-{c}") for c in self.colNameLevel3])
            diffDim = [
                ((pl.col(f"N-{d}-{c}") - meanLogDimN) - (pl.col(f"P-{d}-{c}") - meanLogDimP)) ** 2
                for c in self.colNameLevel3
            ]
            distDimPermExprs.append(pl.sum_horizontal(diffDim).sqrt().alias(f"distPermut_{d}"))

        dfDistPermutDim = logMeansPerm.select(
            pl.col("sampleId"),
            *distDimPermExprs,
        ).sort("sampleId")

        # Observed real distances
        logN = {c: math.log(groupRes.origValues[f"N-{c}"]) for c in self.colNameLevel3}
        logP = {c: math.log(groupRes.origValues[f"P-{c}"]) for c in self.colNameLevel3}
        clrN = {c: logN[c] - sum(logN.values()) / 4.0 for c in self.colNameLevel3}
        clrP = {c: logP[c] - sum(logP.values()) / 4.0 for c in self.colNameLevel3}
        groupRes.origDist = math.sqrt(sum((clrN[c] - clrP[c]) ** 2 for c in self.colNameLevel3))

        groupRes.origDistDim = {}
        for d in self.colNameLevel2:
            logDimN = {c: math.log(groupRes.origDimValues[f"N-{d}-{c}"]) for c in self.colNameLevel3}
            logDimP = {c: math.log(groupRes.origDimValues[f"P-{d}-{c}"]) for c in self.colNameLevel3}
            clrDimN = {c: logDimN[c] - sum(logDimN.values()) / 4.0 for c in self.colNameLevel3}
            clrDimP = {c: logDimP[c] - sum(logDimP.values()) / 4.0 for c in self.colNameLevel3}
            groupRes.origDistDim[d] = math.sqrt(sum((clrDimN[c] - clrDimP[c]) ** 2 for c in self.colNameLevel3))

        k = dfDistPermut.filter(pl.col("distPermut") >= groupRes.origDist).height
        groupRes.pValueGlobal = (k + 1.0) / (self.numPermut + 1.0)

        dimResults = []
        for d in self.colNameLevel2:
            kDim = dfDistPermutDim.filter(pl.col(f"distPermut_{d}") >= groupRes.origDistDim[d]).height
            pValDim = (kDim + 1.0) / (self.numPermut + 1.0)
            decision = "Different" if pValDim <= self.alpha else "Equal"
            dimResults.append({
                "dimension": d,
                "dimensionName": self.dimensionNames[d],
                "observedDistance": round(groupRes.origDistDim[d], 4),
                "pValue": round(pValDim, 5),
                "decision": decision,
            })

        groupRes.dfPermutationResults = pl.DataFrame(dimResults)
        return groupRes

    def run(self) -> None:
        """Run the complete OCAI analysis pipeline for overall and all eligible sub-groups."""
        self.loadAndPreprocess()

        # 1. Overall analysis (entire organization)
        self.overallResult = self._processSubGroup(self.dfPreprocessed, label="Overall")

        # 2. Sub-group analysis if groupBy is defined
        if self.groupByCols:
            self.groupResults = {}
            self.skippedGroups = []

            uniqueLabels = self.dfPreprocessed["groupLabel"].unique().sort().to_list()
            for grpLabel in uniqueLabels:
                dfGrp = self.dfPreprocessed.filter(pl.col("groupLabel") == grpLabel)
                count = dfGrp.height
                if count < self.minGroupSize:
                    self.skippedGroups.append((grpLabel, count))
                else:
                    self.groupResults[grpLabel] = self._processSubGroup(dfGrp, label=grpLabel)

    def getConfidenceIntervalsCfp(self, group: str | None = None) -> pl.DataFrame:
        """Return formatted confidence intervals for the CFP of overall or a specific group."""
        res = self.overallResult if group is None else self.groupResults.get(group)
        if res is None or res.dfIntervalsCfp is None:
            raise RuntimeError(f"Results for group '{group or 'Overall'}' not available. Did you call .run()?")

        rows = []
        for c in self.colNameLevel3:
            rows.append({
                "culture": f"{self.cultureNames[c]} ({c})",
                "nowMin": round(res.dfIntervalsCfp[f"N-{c}_min"][0], 2),
                "nowMean": round(res.origValues[f"N-{c}"], 2),
                "nowMax": round(res.dfIntervalsCfp[f"N-{c}_max"][0], 2),
                "prefMin": round(res.dfIntervalsCfp[f"P-{c}_min"][0], 2),
                "prefMean": round(res.origValues[f"P-{c}"], 2),
                "prefMax": round(res.dfIntervalsCfp[f"P-{c}_max"][0], 2),
            })
        return pl.DataFrame(rows)

    def getAllGroupsConfidenceIntervals(self) -> pl.DataFrame:
        """Return a consolidated DataFrame with CFP confidence intervals for ALL departments."""
        allRes = [self.overallResult] + list(self.groupResults.values())
        dfs = []
        for r in allRes:
            if r is None:
                continue
            dfCfp = self.getConfidenceIntervalsCfp(r.label if r.label != "Overall" else None)
            dfCfp = dfCfp.with_columns(pl.lit(r.label).alias("group"))
            dfCfp = dfCfp.select(["group", "culture", "nowMin", "nowMean", "nowMax", "prefMin", "prefMean", "prefMax"])
            dfs.append(dfCfp)
        return pl.concat(dfs)

    def getAllGroupsDimensionalResults(self) -> pl.DataFrame:
        """Return a consolidated DataFrame with CDP dimensional permutation results for ALL departments."""
        allRes = [self.overallResult] + list(self.groupResults.values())
        dfs = []
        for r in allRes:
            if r is None or r.dfPermutationResults is None:
                continue
            dfCdp = r.dfPermutationResults.with_columns(pl.lit(r.label).alias("group"))
            dfCdp = dfCdp.select(["group", "dimension", "dimensionName", "observedDistance", "pValue", "decision"])
            dfs.append(dfCdp)
        return pl.concat(dfs)

    def getBenchmarkingTable(self) -> pl.DataFrame | None:
        """Return a consolidated benchmarking table comparing Overall and all valid sub-groups."""
        if not self.groupByCols:
            return None

        allRes = [self.overallResult] + list(self.groupResults.values())
        rows = []
        for r in allRes:
            if r is None:
                continue

            nowScores = {self.cultureNames[c]: r.origValues[f"N-{c}"] for c in self.colNameLevel3}
            prefScores = {self.cultureNames[c]: r.origValues[f"P-{c}"] for c in self.colNameLevel3}

            domNow = max(nowScores, key=nowScores.get)
            domPref = max(prefScores, key=prefScores.get)
            decision = "Different" if r.pValueGlobal <= self.alpha else "Equal"

            rows.append({
                "group": r.label,
                "respondents": r.sampleSize,
                "dominantNow": f"{domNow} ({nowScores[domNow]:.1f}%)",
                "dominantPref": f"{domPref} ({prefScores[domPref]:.1f}%)",
                "aitchisonGap": round(r.origDist, 4),
                "pValue": round(r.pValueGlobal, 5),
                "decision": decision,
            })
        return pl.DataFrame(rows)

    def summary(self) -> OcaiSummaryReport:
        """Return an OcaiSummaryReport instance.

        - Can be converted to dict/JSON via .to_dict() for AWS Lambda or REST APIs.
        - Automatically renders rich HTML tables in Jupyter Notebooks via _repr_html_().
        - Formats clean text when printed via print(analyzer.summary()).
        """
        if self.overallResult is None:
            raise RuntimeError("Run analysis first via .run()")

        globalDecision = "DIFFERENT (Reject H0)" if self.overallResult.pValueGlobal <= self.alpha else "EQUAL (Accept H0)"
        globalHypothesis = {
            "observedDistance": round(self.overallResult.origDist, 4),
            "pValue": round(self.overallResult.pValueGlobal, 5),
            "alpha": self.alpha,
            "decision": globalDecision,
        }

        skippedList = [{"group": grp, "respondents": cnt} for grp, cnt in self.skippedGroups]

        return OcaiSummaryReport(
            sampleSize=self.dfRaw.height,
            globalCfp=self.getConfidenceIntervalsCfp(),
            globalHypothesisTest=globalHypothesis,
            dimensionalCdp=self.overallResult.dfPermutationResults,
            benchmarking=self.getBenchmarkingTable(),
            skippedGroups=skippedList,
        )

    # =========================================================================
    # EXPORTING METHODS (Excel, CSV, JSON)
    # =========================================================================

    def exportToExcel(self, filePath: str = "results/ocai_complete_results.xlsx") -> str:
        """Export all individualized department results into a styled multi-sheet Excel workbook."""
        if self.overallResult is None:
            raise RuntimeError("Run analysis first via .run()")

        os.makedirs(os.path.dirname(os.path.abspath(filePath)), exist_ok=True)

        with pl.Config(tbl_rows=-1):
            import pandas as pd
            with pd.ExcelWriter(filePath, engine="openpyxl") as writer:
                # 1. Benchmarking summary
                benchTable = self.getBenchmarkingTable()
                if benchTable is not None:
                    benchTable.to_pandas().to_excel(writer, sheet_name="Benchmarking", index=False)

                # 2. All Groups CFP Confidence Intervals
                self.getAllGroupsConfidenceIntervals().to_pandas().to_excel(writer, sheet_name="Departments_CFP", index=False)

                # 3. All Groups CDP Dimensional Results
                self.getAllGroupsDimensionalResults().to_pandas().to_excel(writer, sheet_name="Departments_CDP", index=False)

                # 4. Overall CFP and CDP
                self.getConfidenceIntervalsCfp().to_pandas().to_excel(writer, sheet_name="Overall_CFP", index=False)
                self.overallResult.dfPermutationResults.to_pandas().to_excel(writer, sheet_name="Overall_CDP", index=False)

        return filePath

    def exportToCsv(self, outputDir: str = "results") -> list[str]:
        """Export individualized results into separate CSV files."""
        if self.overallResult is None:
            raise RuntimeError("Run analysis first via .run()")

        os.makedirs(outputDir, exist_ok=True)
        createdFiles = []

        # Consolidated tables
        benchTable = self.getBenchmarkingTable()
        if benchTable is not None:
            benchPath = os.path.join(outputDir, "benchmarking_summary.csv")
            benchTable.write_csv(benchPath, separator=";")
            createdFiles.append(benchPath)

        allCfpPath = os.path.join(outputDir, "all_departments_cfp.csv")
        self.getAllGroupsConfidenceIntervals().write_csv(allCfpPath, separator=";")
        createdFiles.append(allCfpPath)

        allCdpPath = os.path.join(outputDir, "all_departments_cdp.csv")
        self.getAllGroupsDimensionalResults().write_csv(allCdpPath, separator=";")
        createdFiles.append(allCdpPath)

        # Individualized CSV per department
        deptDir = os.path.join(outputDir, "departments")
        os.makedirs(deptDir, exist_ok=True)

        for grpLabel, res in self.groupResults.items():
            safeLabel = grpLabel.replace(" > ", "_").replace(" ", "_")
            dfCfp = self.getConfidenceIntervalsCfp(grpLabel)
            filePath = os.path.join(deptDir, f"{safeLabel}_cfp.csv")
            dfCfp.write_csv(filePath, separator=";")
            createdFiles.append(filePath)

        return createdFiles

    def exportToJson(self, filePath: str = "results/ocai_summary.json") -> str:
        """Export full structured summary as a JSON file for cloud storage or web dashboards."""
        os.makedirs(os.path.dirname(os.path.abspath(filePath)), exist_ok=True)
        reportDict = self.summary().to_dict()
        with open(filePath, "w", encoding="utf-8") as f:
            json.dump(reportDict, f, indent=2, ensure_ascii=False)
        return filePath

    # =========================================================================
    # PLOTTING METHODS
    # =========================================================================

    def plotOcaiRadar(
        self,
        scoresNow: dict[str, float],
        scoresPref: dict[str, float] | None = None,
        title: str = "OCAI Profile (Competing Values Framework)",
        ciNow: dict[str, tuple[float, float]] | None = None,
        ciPref: dict[str, tuple[float, float]] | None = None,
        ax: plt.Axes | None = None,
    ) -> plt.Axes:
        """Plot a polar radar chart matching Cameron & Quinn's Competing Values Framework."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={"projection": "polar"})

        anglesDeg = [135, 45, 315, 225, 135]
        anglesRad = np.radians(anglesDeg)
        cultOrder = ["A", "B", "C", "D", "A"]

        valNow = [scoresNow[c] for c in cultOrder]

        if ciNow is not None:
            minNow = [ciNow[c][0] for c in cultOrder]
            maxNow = [ciNow[c][1] for c in cultOrder]
            ax.fill_between(anglesRad, minNow, maxNow, color="#1f77b4", alpha=0.15, label="CI Now (95%)")

        if ciPref is not None and scoresPref is not None:
            minPref = [ciPref[c][0] for c in cultOrder]
            maxPref = [ciPref[c][1] for c in cultOrder]
            ax.fill_between(anglesRad, minPref, maxPref, color="#d62728", alpha=0.15, label="CI Preferred (95%)")

        ax.plot(anglesRad, valNow, color="#1f77b4", linewidth=2.5, marker="o", label="Current (Now)")
        ax.fill(anglesRad, valNow, color="#1f77b4", alpha=0.1)

        maxVal = max(valNow)
        if scoresPref is not None:
            valPref = [scoresPref[c] for c in cultOrder]
            ax.plot(anglesRad, valPref, color="#d62728", linewidth=2.5, linestyle="--", marker="s", label="Preferred (Future)")
            ax.fill(anglesRad, valPref, color="#d62728", alpha=0.08)
            maxVal = max(maxVal, max(valPref))

        ax.set_xticks(np.radians([135, 45, 315, 225]))
        ax.set_xticklabels([
            "Clan (A)\n[Internal / Flexible]",
            "Adhocracy (B)\n[External / Flexible]",
            "Market (C)\n[External / Stable]",
            "Hierarchy (D)\n[Internal / Stable]",
        ], fontsize=10, fontweight="bold")

        ax.set_ylim(0, maxVal + 12)
        ax.grid(color="grey", linestyle=":", linewidth=0.7)
        ax.set_title(title, size=13, weight="bold", pad=25)
        ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.15), fontsize=9)

        return ax

    def plotGlobal(self, group: str | None = None, figsize: tuple[int, int] = (7, 7), savePath: str | None = None) -> plt.Figure:
        """Generate and display the CFP radar plot with confidence intervals for overall or a group."""
        res = self.overallResult if group is None else self.groupResults.get(group)
        if res is None:
            raise RuntimeError(f"Group '{group or 'Overall'}' not found.")

        dictNow = {c: res.origValues[f"N-{c}"] for c in self.colNameLevel3}
        dictPref = {c: res.origValues[f"P-{c}"] for c in self.colNameLevel3}

        ciNow = {c: (res.dfIntervalsCfp[f"N-{c}_min"][0], res.dfIntervalsCfp[f"N-{c}_max"][0]) for c in self.colNameLevel3}
        ciPref = {c: (res.dfIntervalsCfp[f"P-{c}_min"][0], res.dfIntervalsCfp[f"P-{c}_max"][0]) for c in self.colNameLevel3}

        fig, ax = plt.subplots(figsize=figsize, subplot_kw={"projection": "polar"})
        lbl = res.label
        self.plotOcaiRadar(
            scoresNow=dictNow,
            scoresPref=dictPref,
            title=f"OCAI Profile: {lbl}\nCurrent vs. Preferred (95% CI)",
            ciNow=ciNow,
            ciPref=ciPref,
            ax=ax,
        )
        plt.tight_layout()
        if savePath:
            plt.savefig(savePath, dpi=300, bbox_inches="tight")
        return fig

    def plotDimensions(self, group: str | None = None, figsize: tuple[int, int] = (16, 11), savePath: str | None = None) -> plt.Figure:
        """Generate and display the 2x3 panel radar plots for all 6 individual dimensions."""
        res = self.overallResult if group is None else self.groupResults.get(group)
        if res is None:
            raise RuntimeError(f"Group '{group or 'Overall'}' not found.")

        fig, axes = plt.subplots(2, 3, figsize=figsize, subplot_kw={"projection": "polar"})
        axes = axes.flatten()

        for idx, d in enumerate(self.colNameLevel2):
            dictDimNow = {c: res.origDimValues[f"N-{d}-{c}"] for c in self.colNameLevel3}
            dictDimPref = {c: res.origDimValues[f"P-{d}-{c}"] for c in self.colNameLevel3}

            pVal = res.dfPermutationResults.filter(pl.col("dimension") == d)["pValue"][0]
            status = f"p={pVal:.3f} (" + ("Diff" if pVal <= self.alpha else "Equal") + ")"

            self.plotOcaiRadar(
                scoresNow=dictDimNow,
                scoresPref=dictDimPref,
                title=f"{self.dimensionNames[d]}\n[{status}]",
                ax=axes[idx],
            )

        lbl = res.label
        plt.suptitle(f"Individual Dimensional Profiles (CDP) - {lbl}", fontsize=16, weight="bold", y=1.02)
        plt.tight_layout()
        if savePath:
            plt.savefig(savePath, dpi=300, bbox_inches="tight")
        return fig

    def plotSubGroupsComparison(self, state: str = "Now", figsize: tuple[int, int] = (8, 8), savePath: str | None = None) -> plt.Figure:
        """Overlay multiple sub-groups on a single radar chart to compare cultural divergence."""
        if not self.groupResults:
            raise RuntimeError("No sub-groups available. Did you pass groupBy and call .run()?")

        prefix = "N" if state.lower() == "now" else "P"
        stateName = "Current (Now)" if prefix == "N" else "Preferred (Future)"

        fig, ax = plt.subplots(figsize=figsize, subplot_kw={"projection": "polar"})

        anglesDeg = [135, 45, 315, 225, 135]
        anglesRad = np.radians(anglesDeg)
        cultOrder = ["A", "B", "C", "D", "A"]

        colors = plt.cm.tab10.colors
        maxVal = 0.0

        for idx, (grpLabel, res) in enumerate(self.groupResults.items()):
            color = colors[idx % len(colors)]
            vals = [res.origValues[f"{prefix}-{c}"] for c in cultOrder]
            maxVal = max(maxVal, max(vals))

            ax.plot(anglesRad, vals, linewidth=2.0, marker="o", color=color, label=f"{grpLabel} (N={res.sampleSize})")
            ax.fill(anglesRad, vals, color=color, alpha=0.06)

        ax.set_xticks(np.radians([135, 45, 315, 225]))
        ax.set_xticklabels([
            "Clan (A)\n[Internal / Flexible]",
            "Adhocracy (B)\n[External / Flexible]",
            "Market (C)\n[External / Stable]",
            "Hierarchy (D)\n[Internal / Stable]",
        ], fontsize=10, fontweight="bold")

        ax.set_ylim(0, maxVal + 12)
        ax.grid(color="grey", linestyle=":", linewidth=0.7)
        ax.set_title(f"Sub-Group Cultural Comparison [{stateName}]", size=14, weight="bold", pad=25)
        ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15), fontsize=9)

        plt.tight_layout()
        if savePath:
            plt.savefig(savePath, dpi=300, bbox_inches="tight")
        return fig
