# SyncroSim Core Bug: Environment Variables Not Passed to Conda Transformers in Docker

## Problem Summary

When SyncroSim runs transformers using conda environments inside Docker containers, it fails to pass required `SSIM_*` environment variables to the Python subprocess. This causes all transformers to fail with missing environment data.

## Environment

- **Platform**: Docker container (Linux)
- **SyncroSim**: Launched via `mono /syncrosim/SyncroSim.Console.exe`
- **Python Environment**: Conda environment (`omniscape-3.5`)
- **pysyncrosim**: Latest version with environment validation

## Reproduction

1. Run SyncroSim in a Docker container
2. Configure a transformer to use a conda environment
3. Execute a simulation that calls the transformer
4. Transformer fails with missing environment variables

## Expected Behavior

When SyncroSim launches a transformer, it should pass these environment variables to the subprocess:

```bash
SSIM_PROGRAM_DIRECTORY=/syncrosim
SSIM_LIBRARY_FILEPATH=/path/to/library.ssim
SSIM_DATA_DIRECTORY=/path/to/scenario/data
SSIM_TEMP_DIRECTORY=/path/to/temp
SSIM_TRANSFER_DIRECTORY=/path/to/transfer
SSIM_PROJECT_ID=1
SSIM_SCENARIO_ID=12
```

These variables are essential for transformers to:
- Access scenario data
- Create temporary files
- Write outputs
- Report progress back to SyncroSim

## Actual Behavior

**None of the `SSIM_*` environment variables are set** when the Python process starts.

### Evidence

```
Working directory: None
```

This output from the Omniscape transformer shows that `ps.environment._environment().data_directory` returns `None`, confirming `SSIM_DATA_DIRECTORY` is not set.

### Error Trace

```python
Traceback (most recent call last):
  File "/syncrosim/Packages/omniscape/2.6.0/omniscapeTransformer.py", line 81
    if os.path.exists(wrkDir) == False:
       ^^^^^^^^^^^^^^^^^^^^^^
TypeError: stat: path should be string, bytes, os.PathLike or integer, not NoneType
```

The transformer receives `None` because pysyncrosim reads from `os.getenv("SSIM_DATA_DIRECTORY")`, which returns `None`.

## Root Cause

When SyncroSim activates a conda environment to run a transformer, the subprocess launch mechanism does not preserve/pass the `SSIM_*` environment variables.

Likely causes:
1. **Conda activation overwrites environment**: The conda activate command may be clearing the environment
2. **Subprocess not inheriting environment**: The way Python is launched may not preserve parent environment variables
3. **Docker environment isolation**: Environment variables may not be passed through container boundaries properly

## Impact

- **All conda-based transformers fail in Docker**
- Transformers cannot access scenario data
- Progress reporting breaks
- Temporary file creation fails
- Makes SyncroSim unusable in containerized environments

## Suggested Fix

### Option 1: Explicit Environment Passthrough (Recommended)

When launching the transformer subprocess, explicitly pass all `SSIM_*` environment variables:

```python
import subprocess
import os

# Collect SSIM environment variables
ssim_env = {k: v for k, v in os.environ.items() if k.startswith('SSIM_')}

# Launch transformer with environment
subprocess.Popen(
    [conda_python, transformer_script],
    env={**os.environ, **ssim_env}  # Merge current env with SSIM vars
)
```

### Option 2: Pre-activation Environment Setup

Before activating conda, export all `SSIM_*` variables so they persist through activation:

```bash
# Set variables before conda activate
export SSIM_PROGRAM_DIRECTORY=/syncrosim
export SSIM_LIBRARY_FILEPATH=/path/to/library.ssim
# ... etc

# Then activate conda
source activate omniscape-3.5

# Then run transformer
python transformer.py
```

### Option 3: Conda Environment Variable Configuration

Configure conda to preserve specific environment variables during activation:

```yaml
# In the conda environment or condarc
env_vars:
  SSIM_PROGRAM_DIRECTORY: ${SSIM_PROGRAM_DIRECTORY}
  SSIM_LIBRARY_FILEPATH: ${SSIM_LIBRARY_FILEPATH}
  # ... etc
```

## Testing & Verification

To verify the fix works, add this diagnostic code to any transformer:

```python
import os
print("=== SyncroSim Environment Check ===")
required_vars = ['SSIM_PROGRAM_DIRECTORY', 'SSIM_LIBRARY_FILEPATH',
                 'SSIM_DATA_DIRECTORY', 'SSIM_TEMP_DIRECTORY',
                 'SSIM_PROJECT_ID', 'SSIM_SCENARIO_ID']
for var in required_vars:
    value = os.getenv(var)
    print(f"{var}: {value if value else 'MISSING'}")
```

All variables should show values, not "MISSING".

## Workaround (Temporary)

Until this is fixed in SyncroSim Core, users can:
1. Manually set `SSIM_*` variables in their Dockerfile
2. Use a wrapper script that preserves environment variables
3. Avoid using conda environments (not recommended)

However, these workarounds are fragile and don't work for dynamically-created variables like `SSIM_DATA_DIRECTORY`.

## Related Information

- **SyncroSim Version**: (please specify version being tested)
- **Python Version**: 3.12
- **Conda Version**: Latest miniconda3
- **OS**: Linux (MINGW64_NT-10.0-26200 on host)

## Contact

For questions about this issue, contact the pysyncrosim development team.
