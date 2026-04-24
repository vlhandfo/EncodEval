#!/bin/bash

# Run finetuning and eval for a task and model

#SBATCH --job-name=EncodEval
#SBATCH --account=project_465002893
#SBATCH --time=1:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus=1
#SBATCH --mem=32G
#SBATCH --partition=dev-g
#SBATCH --output=slurm_logs/%x-%j.out
#SBATCH --error=slurm_logs/%x-%j.err

set -euo pipefail

export VENV=/scratch/project_465002893/nb-embed/EncodEval/.venv/
export SIF=/appl/local/laifs/containers/lumi-multitorch-u24r64f21m43t29-20260225_144743/lumi-multitorch-full-u24r64f21m43t29-20260225_144743.sif

mkdir -p slurm_logs

module use /appl/local/laifs/modules
module load lumi-aif-singularity-bindings/1.0.0

export HIP_VISIBLE_DEVICES=0
export TORCH_COMPILE_DISABLE=1

export MODEL_PATH="${MODEL_PATH:-/scratch/project_465002893/nb-embed/EuroBERT/hf_modeling/base_50k}"
export CONFIG_FILE="${CONFIG_FILE:-/scratch/project_465002893/nb-embed/EncodEval/configs/sequence_classification_tasks/norec_nb_test.yaml}"


singularity exec -B "$VENV":/user-software "$SIF" /user-software/bin/python /scratch/project_465002893/nb-embed/EncodEval/main.py --model_path $MODEL_PATH --config_file $CONFIG_FILE
