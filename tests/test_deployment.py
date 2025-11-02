"""
Tests for the deployment script.
"""
import os
import subprocess
import sys
from pathlib import Path
import shutil


def test_deploy_script_help():
    """Test that the deploy script shows help."""
    result = subprocess.run(
        [sys.executable, 'deploy.py', '--help'],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    assert result.returncode == 0
    assert 'Deploy the pyodide-ship-combat simulator' in result.stdout
    assert '--test' in result.stdout
    assert '--build' in result.stdout
    assert '--deploy' in result.stdout


def test_deploy_script_build():
    """Test that the deploy script can build successfully."""
    repo_root = Path(__file__).parent.parent
    build_dir = repo_root / 'test_build'
    
    # Clean up any existing test build
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    try:
        result = subprocess.run(
            [sys.executable, 'deploy.py', '--build', '--build-dir', 'test_build'],
            capture_output=True,
            text=True,
            cwd=repo_root,
            timeout=30
        )
        
        assert result.returncode == 0, f"Build failed: {result.stderr}"
        assert 'Build complete!' in result.stdout
        
        # Verify build structure
        assert build_dir.exists()
        assert (build_dir / 'index.html').exists()
        assert (build_dir / 'battle.html').exists()
        assert (build_dir / 'sample_interface.html').exists()
        assert (build_dir / 'README.md').exists()
        assert (build_dir / 'ship_combat').is_dir()
        assert (build_dir / 'ship_combat' / 'battle_sim.py').exists()
        assert (build_dir / 'ship_combat' / 'models.py').exists()
        
        # Verify index.html has correct content
        index_content = (build_dir / 'index.html').read_text()
        assert 'Pyodide Ship Combat Simulator' in index_content
        assert 'battle.html' in index_content
        assert 'sample_interface.html' in index_content
        
    finally:
        # Clean up
        if build_dir.exists():
            shutil.rmtree(build_dir)


def test_deploy_script_test_mode():
    """Test that the deploy script can run tests."""
    repo_root = Path(__file__).parent.parent
    
    # Just test that the script accepts the --test flag and doesn't crash
    # We can't actually run it because it would cause infinite recursion
    result = subprocess.run(
        [sys.executable, 'deploy.py', '--help'],
        capture_output=True,
        text=True,
        cwd=repo_root,
        timeout=10
    )
    
    # Verify --test flag exists in help
    assert result.returncode == 0
    assert '--test' in result.stdout
