import pytest
from backend.experiments import ab_experiment_engine

def test_1000_session_ab_experiment_simulation():
    res = ab_experiment_engine.generate_benchmark_dataset(n_sessions=1000)
    assert res["total_sessions_simulated"] == 1000
    
    control = res["control_metrics"]
    treatment = res["treatment_metrics"]
    uplift = res["uplift_metrics"]
    
    assert control["sessions"] == 500
    assert treatment["sessions"] == 500
    
    # Verify AI Treatment outperforms Control
    assert treatment["conversion_rate"] > control["conversion_rate"]
    assert treatment["aov"] > control["aov"]
    assert treatment["total_revenue"] > control["total_revenue"]
    assert treatment["revenue_per_session"] > control["revenue_per_session"]
    assert "incremental_revenue_gained" in uplift
