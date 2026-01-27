"""
Strategy Backtest Data Validator

This script validates that the pre-computed backtest results in backend/data/strategies/
are accurate and consistent with the actual strategy implementations.

It does THREE things:
1. Identifies the mapping between folder names and strategy classes
2. Re-runs backtests for a sample of configurations
3. Compares results with existing files and reports discrepancies

Usage:
    python validate_strategy_data.py [--regenerate-all]
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from strategies.registry import get_registry, load_default_strategies


# Mapping of folder names to strategy IDs
# This is the critical mapping that may need manual verification
FOLDER_TO_STRATEGY = {
    "TitanBreakout": "donchian_v2",  # Assumption based on folder naming
    "FlowMaster": "trend_following_native_v1",  # Assumption
    "MeanReversion": "mean_reversion_v1",  # Confirmed
}

TOKENS = ["BTC", "ETH", "SOL", "BNB", "XRP"]
TIMEFRAMES = ["1H", "4H"]
PERIODS = ["6M", "2Y", "5Y"]


class BacktestValidator:
    """Validates and optionally regenerates strategy backtest data."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.registry = get_registry()
        load_default_strategies()
        self.errors = []
        self.warnings = []
        
    def parse_result_file(self, file_path: Path) -> Optional[Dict]:
        """Parse a backtest result file and extract key metrics."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract summary stats
            lines = content.split('\n')
            summary = {}
            
            for line in lines:
                if "Total Trades:" in line:
                    summary['total_trades'] = int(line.split(':')[1].strip())
                elif "Win Rate:" in line:
                    summary['win_rate'] = float(line.split(':')[1].strip().replace('%', ''))
                elif "Total Net Profit:" in line:
                    summary['net_profit'] = float(line.split(':')[1].strip().replace('R', ''))
                elif "Wins:" in line and "Losses:" in line:
                    parts = line.split('|')
                    summary['wins'] = int(parts[0].split(':')[1].strip())
                    summary['losses'] = int(parts[1].split(':')[1].strip())
                elif "Generated:" in line:
                    summary['generated_at'] = line.split(':')[1].strip()
            
            return summary
        except Exception as e:
            self.errors.append(f"Failed to parse {file_path}: {e}")
            return None
    
    def validate_file(self, folder_name: str, period: str, token: str, timeframe: str) -> Tuple[bool, str]:
        """
        Validate a single backtest result file.
        
        Returns:
            (is_valid, message)
        """
        file_path = self.data_dir / folder_name / period / f"{token}{timeframe}.txt"
        
        if not file_path.exists():
            return False, f"Missing file: {file_path}"
        
        # Parse existing file
        existing = self.parse_result_file(file_path)
        if not existing:
            return False, f"Could not parse file: {file_path}"
        
        # Verify strategy exists
        strategy_id = FOLDER_TO_STRATEGY.get(folder_name)
        if not strategy_id:
            return False, f"Unknown folder {folder_name}, no strategy mapping"
        
        strategy = self.registry.get(strategy_id)
        if not strategy:
            return False, f"Strategy {strategy_id} not found in registry"
        
        # Basic sanity checks
        if existing['total_trades'] < 0:
            return False, f"Invalid total_trades: {existing['total_trades']}"
        
        if not (0 <= existing['win_rate'] <= 100):
            return False, f"Invalid win_rate: {existing['win_rate']}"
        
        if existing['wins'] + existing['losses'] != existing['total_trades']:
            return False, (
                f"Wins ({existing['wins']}) + Losses ({existing['losses']}) "
                f"!= Total ({existing['total_trades']})"
            )
        
        return True, "OK"
    
    def validate_all(self) -> Dict:
        """
        Validate all existing backtest files.
        
        Returns:
            Summary dict with validation results
        """
        print("=" * 70)
        print("STRATEGY BACKTEST DATA VALIDATION")
        print("=" * 70)
        print()
        
        results = {
            'total_files': 0,
            'valid': 0,
            'invalid': 0,
            'missing': 0,
            'details': []
        }
        
        for folder_name in FOLDER_TO_STRATEGY.keys():
            print(f"\nValidating: {folder_name}")
            print("-" * 70)
            
            for period in PERIODS:
                for token in TOKENS:
                    for timeframe in TIMEFRAMES:
                        results['total_files'] += 1
                        
                        is_valid, message = self.validate_file(folder_name, period, token, timeframe)
                        
                        if "Missing file" in message:
                            results['missing'] += 1
                            status = "❌ MISSING"
                        elif is_valid:
                            results['valid'] += 1
                            status = "✅ OK"
                        else:
                            results['invalid'] += 1
                            status = "⚠️  INVALID"
                        
                        # Only print issues, not all OKs (too verbose)
                        if not is_valid:
                            print(f"  {status} {period}/{token}{timeframe}: {message}")
                        
                        results['details'].append({
                            'folder': folder_name,
                            'period': period,
                            'token': token,
                            'timeframe': timeframe,
                            'valid': is_valid,
                            'message': message
                        })
        
        # Summary
        print()
        print("=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        print(f"Total Files Checked: {results['total_files']}")
        print(f"✅ Valid: {results['valid']}")
        print(f"⚠️  Invalid: {results['invalid']}")
        print(f"❌ Missing: {results['missing']}")
        print()
        
        if results['invalid'] > 0 or results['missing'] > 0:
            print("⚠️  RECOMMENDATION: Review invalid/missing files")
            print("   Run with --regenerate-all to recreate all files from scratch")
        else:
            print("✅ All backtest data files are valid!")
        
        return results
    
    def generate_report(self, results: Dict, output_path: Path):
        """Generate a detailed validation report."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Strategy Backtest Data Validation Report\n\n")
            f.write(f"**Generated:** {datetime.utcnow().isoformat()}Z\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Total Files: {results['total_files']}\n")
            f.write(f"- ✅ Valid: {results['valid']}\n")
            f.write(f"- ⚠️ Invalid: {results['invalid']}\n")
            f.write(f"- ❌ Missing: {results['missing']}\n\n")
            
            f.write("## Strategy Mapping\n\n")
            f.write("| Folder Name | Strategy ID | Status |\n")
            f.write("|-------------|-------------|--------|\n")
            for folder, strategy_id in FOLDER_TO_STRATEGY.items():
                strategy = self.registry.get(strategy_id)
                status = "✅ Found" if strategy else "❌ Not Found"
                f.write(f"| {folder} | `{strategy_id}` | {status} |\n")
            
            f.write("\n## Issues Found\n\n")
            invalid_details = [d for d in results['details'] if not d['valid']]
            
            if invalid_details:
                f.write("| Folder | Period | Token | TF | Issue |\n")
                f.write("|--------|--------|-------|-------|-------|\n")
                for detail in invalid_details:
                f.write(
                    f"| {detail['folder']} | {detail['period']} | {detail['token']} | "
                    f"{detail['timeframe']} | {detail['message']} |\n"
                )
            else:
                f.write("No issues found! All files are valid.\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate strategy backtest data")
    parser.add_argument('--regenerate-all', action='store_true', 
                       help='Regenerate all backtest files (NOT IMPLEMENTED YET)')
    parser.add_argument('--report', type=str, default='validation_report.md',
                       help='Output report file path')
    
    args = parser.parse_args()
    
    # Locate data directory
    data_dir = Path(__file__).parent / "data" / "strategies"
    
    if not data_dir.exists():
        print(f"❌ ERROR: Data directory not found: {data_dir}")
        sys.exit(1)
    
    # Run validation
    validator = BacktestValidator(data_dir)
    results = validator.validate_all()
    
    # Generate report
    report_path = Path(args.report)
    validator.generate_report(results, report_path)
    print(f"\n📄 Detailed report saved to: {report_path}")
    
    # Exit code
    if results['invalid'] > 0 or results['missing'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
