import sys
sys.path.insert(0, 'C:/Users/hp/Desktop/gen ai/backend')
from app.tools.company_resolver import CompanyResolver
from app.core.orchestrator import DynamicOrchestrator

print(CompanyResolver.resolve('Google'))
print(CompanyResolver.resolve('NVIDIA'))
report = DynamicOrchestrator().run_investigation('NVIDIA', max_iterations=3)
print(report.company_name)
print(report.ticker)
print(report.dcf_result.intrinsic_value_per_share)
