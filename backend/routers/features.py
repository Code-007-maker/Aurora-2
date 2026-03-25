from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/features", tags=["Feature Engineering"])

class GridFeatureRequest(BaseModel):
    grid_id: str
    elevation: float
    slope: float
    drainage_distance_m: float
    impervious_area_sqm: float
    rainfall_mm: float = None # Allow missing, fallback to avg
    population: int = None # Allow missing, fallback to ward dist
    infrastructure_count: int = 0
    ward_drainage_efficiency: float = 0.8 # New: Operational readiness score of drains (from readiness API)

class NormalizedFeatures(BaseModel):
    grid_id: str
    elevation_score: float
    slope_gradient: float
    drainage_proximity_index: float
    impervious_surface_ratio: float
    rainfall_intensity_index: float
    population_exposure_index: float
    infrastructure_vulnerability_score: float
    capacity_exceedance_ratio: float # New: Critical GIS metric
    effective_drainage_capacity_mm_hr: float # New: Dynamic capacity

@router.post("/calculate", response_model=List[NormalizedFeatures])
async def calculate_features(requests: List[GridFeatureRequest]):
    """
    Computes and normalizes (0-1) feature engineering metrics per micro-grid.
    Addresses edge cases like missing rainfall or population data.
    """
    results = []
    
    # Constants for normalization (In a real system, these would be derived from data max/min)
    MAX_ELEV = 500.0  # meters
    MAX_SLOPE = 45.0  # degrees
    MAX_DRAINAGE_DIST = 5000.0 # meters
    CELL_AREA = 10000.0 # 100m x 100m
    AVG_RAINFALL = 100.0 # mm fallback
    MAX_RAINFALL = 300.0 # mm
    AVG_POP = 50 # persons per cell fallback
    MAX_POP = 1000 
    MAX_INFRA = 10
    
    # GIS Drainage Constants
    BASE_DRAIN_CAPACITY_MM_HR = 50.0  # Assumed standard engineering capacity of nearest main drain
    
    for req in requests:
        # Edge cases fallback
        rainfall = req.rainfall_mm if req.rainfall_mm is not None else AVG_RAINFALL
        population = req.population if req.population is not None else AVG_POP
        
        # Zero drainage handling
        drainage_dist = req.drainage_distance_m if req.drainage_distance_m > 0 else MAX_DRAINAGE_DIST
        
        # 1. Elevation Score (Lower elevation -> higher risk/score)
        elev_score = max(0.0, 1.0 - (min(req.elevation, MAX_ELEV) / MAX_ELEV))
        
        # 2. Slope Gradient (Flatter slope -> higher pooling risk/score)
        slope_score = max(0.0, 1.0 - (min(req.slope, MAX_SLOPE) / MAX_SLOPE))
        
        # 3. Drainage Proximity (Further from drainage -> higher risk)
        drainage_score = min(drainage_dist, MAX_DRAINAGE_DIST) / MAX_DRAINAGE_DIST
        
        # 4. Impervious surface ratio (More impervious -> higher runoff/risk)
        impervious_score = min(req.impervious_area_sqm / CELL_AREA, 1.0)
        
        # 5. Rainfall intensity
        rainfall_score = min(rainfall / MAX_RAINFALL, 1.0)
        
        # 6. Population exposure
        pop_score = min(population / MAX_POP, 1.0)
        
        # 7. Infrastructure vulnerability
        infra_score = min(req.infrastructure_count / MAX_INFRA, 1.0)
        
        # --- NEW GIS DRAINAGE CAPACITY LOGIC ---
        
        # A. Calculate Effective Drainage Capacity (EDC)
        # Reduced by GIS proximity (if you are far away, effective capacity drops)
        # Reuced by Operational efficiency (if drains are clogged, capacity drops)
        effective_capacity = BASE_DRAIN_CAPACITY_MM_HR * (1.0 - drainage_score) * req.ward_drainage_efficiency
        effective_capacity = max(effective_capacity, 1.0) # Prevent division by zero
        
        # B. Calculate required capacity (Inflow Volume)
        # Water that cannot be absorbed immediately by the ground
        # (Rainfall * Area * Impervious Ratio) relative to the unit area
        inflow_mm_hr = rainfall * impervious_score
        
        # C. Calculate Capacity Exceedance Ratio
        # If > 1.0, the water is arriving faster than the drains can clear it = Flash Flood
        exceedance_ratio = inflow_mm_hr / effective_capacity
        
        # Normalize exceedance for the ML Model (Cap at extremely flooded -> 3.0, scale to 0-1)
        normalized_exceedance = min(exceedance_ratio / 3.0, 1.0)
        
        results.append(NormalizedFeatures(
            grid_id=req.grid_id,
            elevation_score=round(elev_score, 4),
            slope_gradient=round(slope_score, 4),
            drainage_proximity_index=round(drainage_score, 4),
            impervious_surface_ratio=round(impervious_score, 4),
            rainfall_intensity_index=round(rainfall_score, 4),
            population_exposure_index=round(pop_score, 4),
            infrastructure_vulnerability_score=round(infra_score, 4),
            capacity_exceedance_ratio=round(normalized_exceedance, 4),
            effective_drainage_capacity_mm_hr=round(effective_capacity, 2)
        ))
        
    return results
