#!/usr/bin/env python3
"""
Data Science Test Runner for Jupyter + SQL challenges
Handles execution and validation of data science code submissions
"""

import json
import sys
import os
import tempfile
import traceback
import subprocess
import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from pathlib import Path
import warnings
import contextlib
from io import StringIO

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class DataTestRunner:
    """Test runner for data science challenges"""
    
    def __init__(self):
        self.workspace = Path("/workspace")
        self.datasets_dir = Path("/datasets")
        self.results = []
        
    def run_python_analysis(self, code: str, test_config: Dict) -> Dict:
        """Run Python data analysis code and validate results"""
        
        result = {
            "type": "python_analysis",
            "passed": False,
            "score": 0,
            "max_score": 100,
            "output": "",
            "error": "",
            "validations": []
        }
        
        try:
            # Create isolated namespace
            namespace = {
                'pd': pd,
                'np': np,
                'plt': None,  # Will import matplotlib if needed
                'sns': None,  # Will import seaborn if needed
            }
            
            # Load required dataset if specified
            if 'dataset' in test_config:
                dataset_path = self.datasets_dir / test_config['dataset']
                if dataset_path.exists():
                    if dataset_path.suffix == '.csv':
                        namespace['df'] = pd.read_csv(dataset_path)
                    elif dataset_path.suffix in ['.xlsx', '.xls']:
                        namespace['df'] = pd.read_excel(dataset_path)
                    else:
                        raise ValueError(f"Unsupported dataset format: {dataset_path.suffix}")
            
            # Capture stdout/stderr
            captured_output = StringIO()
            
            with contextlib.redirect_stdout(captured_output):
                with contextlib.redirect_stderr(captured_output):
                    # Execute the code
                    exec(code, namespace)
            
            result["output"] = captured_output.getvalue()
            
            # Run validations
            validations = test_config.get('validations', [])
            passed_validations = 0
            
            for validation in validations:
                validation_result = self._run_validation(validation, namespace)
                result["validations"].append(validation_result)
                if validation_result["passed"]:
                    passed_validations += 1
            
            # Calculate score
            if validations:
                result["score"] = int((passed_validations / len(validations)) * 100)
                result["passed"] = passed_validations == len(validations)
            else:
                result["passed"] = True
                result["score"] = 100
                
        except Exception as e:
            result["error"] = f"Execution error: {str(e)}\n{traceback.format_exc()}"
            result["passed"] = False
            result["score"] = 0
            
        return result
    
    def run_sql_query(self, query: str, test_config: Dict) -> Dict:
        """Run SQL query against test database and validate results"""
        
        result = {
            "type": "sql_query",
            "passed": False,
            "score": 0,
            "max_score": 100,
            "output": "",
            "error": "",
            "rows_returned": 0,
            "validations": []
        }
        
        try:
            # Create in-memory database or connect to existing
            db_path = ":memory:"
            if 'database' in test_config:
                db_path = self.datasets_dir / test_config['database']
            
            conn = sqlite3.connect(db_path)
            
            # Load sample data if specified
            if 'setup_sql' in test_config:
                conn.executescript(test_config['setup_sql'])
            
            # Execute the query
            df = pd.read_sql_query(query, conn)
            result["rows_returned"] = len(df)
            result["output"] = df.to_string(index=False) if len(df) > 0 else "No rows returned"
            
            # Run validations
            validations = test_config.get('validations', [])
            passed_validations = 0
            
            for validation in validations:
                validation_result = self._run_sql_validation(validation, df, conn)
                result["validations"].append(validation_result)
                if validation_result["passed"]:
                    passed_validations += 1
            
            # Calculate score
            if validations:
                result["score"] = int((passed_validations / len(validations)) * 100)
                result["passed"] = passed_validations == len(validations)
            else:
                result["passed"] = len(df) > 0  # Default: query should return data
                result["score"] = 100 if result["passed"] else 0
            
            conn.close()
            
        except Exception as e:
            result["error"] = f"SQL error: {str(e)}\n{traceback.format_exc()}"
            result["passed"] = False
            result["score"] = 0
            
        return result
    
    def run_jupyter_notebook(self, notebook_content: str, test_config: Dict) -> Dict:
        """Execute Jupyter notebook and validate outputs"""
        
        result = {
            "type": "jupyter_notebook",
            "passed": False,
            "score": 0,
            "max_score": 100,
            "output": "",
            "error": "",
            "cell_outputs": [],
            "validations": []
        }
        
        try:
            # Create temporary notebook file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ipynb', delete=False) as f:
                f.write(notebook_content)
                notebook_path = f.name
            
            # Execute notebook using nbconvert
            cmd = [
                'jupyter', 'nbconvert',
                '--to', 'notebook',
                '--execute',
                '--output-dir', '/tmp',
                notebook_path
            ]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
                cwd='/workspace'
            )
            
            if process.returncode != 0:
                result["error"] = f"Notebook execution failed: {process.stderr}"
                return result
            
            # Read executed notebook
            executed_notebook_path = notebook_path.replace('.ipynb', '.nbconvert.ipynb')
            with open(executed_notebook_path, 'r') as f:
                executed_notebook = json.load(f)
            
            # Extract outputs from cells
            for i, cell in enumerate(executed_notebook.get('cells', [])):
                if cell.get('cell_type') == 'code':
                    outputs = cell.get('outputs', [])
                    cell_result = {
                        "cell_index": i,
                        "outputs": [str(output) for output in outputs],
                        "execution_count": cell.get('execution_count')
                    }
                    result["cell_outputs"].append(cell_result)
            
            # Run validations
            validations = test_config.get('validations', [])
            passed_validations = 0
            
            for validation in validations:
                validation_result = self._run_notebook_validation(validation, executed_notebook)
                result["validations"].append(validation_result)
                if validation_result["passed"]:
                    passed_validations += 1
            
            # Calculate score
            if validations:
                result["score"] = int((passed_validations / len(validations)) * 100)
                result["passed"] = passed_validations == len(validations)
            else:
                result["passed"] = True
                result["score"] = 100
            
            result["output"] = f"Notebook executed successfully with {len(result['cell_outputs'])} code cells"
            
            # Cleanup
            os.unlink(notebook_path)
            if os.path.exists(executed_notebook_path):
                os.unlink(executed_notebook_path)
                
        except Exception as e:
            result["error"] = f"Notebook error: {str(e)}\n{traceback.format_exc()}"
            result["passed"] = False
            result["score"] = 0
            
        return result
    
    def _run_validation(self, validation: Dict, namespace: Dict) -> Dict:
        """Run a validation check on Python analysis results"""
        
        validation_result = {
            "name": validation.get("name", "Unnamed validation"),
            "passed": False,
            "message": ""
        }
        
        try:
            validation_type = validation.get("type", "")
            
            if validation_type == "variable_exists":
                var_name = validation["variable"]
                if var_name in namespace:
                    validation_result["passed"] = True
                    validation_result["message"] = f"Variable '{var_name}' exists"
                else:
                    validation_result["message"] = f"Variable '{var_name}' not found"
            
            elif validation_type == "dataframe_shape":
                df_name = validation.get("dataframe", "df")
                expected_shape = validation["shape"]
                if df_name in namespace:
                    actual_shape = namespace[df_name].shape
                    if actual_shape == tuple(expected_shape):
                        validation_result["passed"] = True
                        validation_result["message"] = f"DataFrame shape {actual_shape} is correct"
                    else:
                        validation_result["message"] = f"Expected shape {expected_shape}, got {actual_shape}"
                else:
                    validation_result["message"] = f"DataFrame '{df_name}' not found"
            
            elif validation_type == "value_check":
                var_name = validation["variable"]
                expected_value = validation["expected"]
                if var_name in namespace:
                    actual_value = namespace[var_name]
                    if np.isclose(actual_value, expected_value, rtol=1e-3) if isinstance(actual_value, (int, float)) else actual_value == expected_value:
                        validation_result["passed"] = True
                        validation_result["message"] = f"Value {actual_value} matches expected {expected_value}"
                    else:
                        validation_result["message"] = f"Expected {expected_value}, got {actual_value}"
                else:
                    validation_result["message"] = f"Variable '{var_name}' not found"
            
            elif validation_type == "custom_check":
                check_code = validation["check"]
                try:
                    result = eval(check_code, namespace)
                    validation_result["passed"] = bool(result)
                    validation_result["message"] = f"Custom check {'passed' if result else 'failed'}: {check_code}"
                except Exception as e:
                    validation_result["message"] = f"Custom check error: {str(e)}"
            
        except Exception as e:
            validation_result["message"] = f"Validation error: {str(e)}"
        
        return validation_result
    
    def _run_sql_validation(self, validation: Dict, result_df: pd.DataFrame, conn) -> Dict:
        """Run validation check on SQL query results"""
        
        validation_result = {
            "name": validation.get("name", "Unnamed validation"),
            "passed": False,
            "message": ""
        }
        
        try:
            validation_type = validation.get("type", "")
            
            if validation_type == "row_count":
                expected_count = validation["expected"]
                actual_count = len(result_df)
                if actual_count == expected_count:
                    validation_result["passed"] = True
                    validation_result["message"] = f"Returned {actual_count} rows as expected"
                else:
                    validation_result["message"] = f"Expected {expected_count} rows, got {actual_count}"
            
            elif validation_type == "column_exists":
                column_name = validation["column"]
                if column_name in result_df.columns:
                    validation_result["passed"] = True
                    validation_result["message"] = f"Column '{column_name}' exists"
                else:
                    validation_result["message"] = f"Column '{column_name}' not found"
            
            elif validation_type == "value_in_result":
                expected_value = validation["value"]
                column = validation.get("column")
                if column:
                    found = expected_value in result_df[column].values
                else:
                    found = expected_value in result_df.values
                
                validation_result["passed"] = found
                validation_result["message"] = f"Value {expected_value} {'found' if found else 'not found'} in results"
            
        except Exception as e:
            validation_result["message"] = f"Validation error: {str(e)}"
        
        return validation_result
    
    def _run_notebook_validation(self, validation: Dict, notebook: Dict) -> Dict:
        """Run validation check on notebook execution results"""
        
        validation_result = {
            "name": validation.get("name", "Unnamed validation"),
            "passed": False,
            "message": ""
        }
        
        try:
            validation_type = validation.get("type", "")
            
            if validation_type == "cell_executed":
                cell_index = validation["cell"]
                cells = notebook.get("cells", [])
                if cell_index < len(cells) and cells[cell_index].get("execution_count") is not None:
                    validation_result["passed"] = True
                    validation_result["message"] = f"Cell {cell_index} executed successfully"
                else:
                    validation_result["message"] = f"Cell {cell_index} was not executed"
            
            elif validation_type == "output_contains":
                text = validation["text"]
                cells = notebook.get("cells", [])
                found = False
                for cell in cells:
                    for output in cell.get("outputs", []):
                        output_text = str(output)
                        if text in output_text:
                            found = True
                            break
                    if found:
                        break
                
                validation_result["passed"] = found
                validation_result["message"] = f"Text '{text}' {'found' if found else 'not found'} in outputs"
            
        except Exception as e:
            validation_result["message"] = f"Validation error: {str(e)}"
        
        return validation_result


def main():
    """Main test runner entry point"""
    
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No test configuration provided"}))
        sys.exit(1)
    
    try:
        test_config = json.loads(sys.argv[1])
        runner = DataTestRunner()
        
        challenge_type = test_config.get("type", "python")
        code = test_config.get("code", "")
        
        if challenge_type == "python":
            result = runner.run_python_analysis(code, test_config)
        elif challenge_type == "sql":
            result = runner.run_sql_query(code, test_config)
        elif challenge_type == "jupyter":
            result = runner.run_jupyter_notebook(code, test_config)
        else:
            result = {
                "error": f"Unknown challenge type: {challenge_type}",
                "passed": False,
                "score": 0
            }
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        error_result = {
            "error": f"Test runner error: {str(e)}\n{traceback.format_exc()}",
            "passed": False,
            "score": 0
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()