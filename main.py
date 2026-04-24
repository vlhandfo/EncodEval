import json
import os
import subprocess

import configue
import fire
import wandb

from datetime import datetime
from encodeval.eval_tasks import (
    EvalConfig,
    SequenceClassificationEval,
    SequenceRegressionEval,
    TokenClassificationEval,
    RetrievalEval,
)


def main(config_file: str = None, model_path: str = None):
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["EVAL_MODEL_PATH"] = model_path
    print(f"Evaluating model at path: {model_path}")
    eval_config: EvalConfig = configue.load(config_file, sub_path="eval_config")

    run = wandb.init(
        entity="nbailab",
        project="nb-embed-encodeval", 
        name=config_file.split("/")[-1].replace(".yaml", ""),
        )

    # Determine the evaluator based on task type
    if eval_config.task_type == "SC":
        evaluator = SequenceClassificationEval(eval_config)
    elif eval_config.task_type == "SR":
        evaluator = SequenceRegressionEval(eval_config)
    elif eval_config.task_type == "TC":
        evaluator = TokenClassificationEval(eval_config)
    elif eval_config.task_type == "IR":
        evaluator = RetrievalEval(eval_config)
    else:
        raise ValueError(f"Invalid task type: {eval_config.task_type}")
    
    # Run training if needed
    if eval_config.tr_args.do_train:            
        if os.path.exists(eval_config.tr_args.output_dir) and len(os.listdir(eval_config.tr_args.output_dir)) > 0:
            print(f"A fine-tuned model already exists for this configuration at {eval_config.tr_args.output_dir}, skipping training") 
        else:
            evaluator.train()
    else:
        print("Training disabled, skipping training")
    
    # Run evaluation
    results = {}
    if eval_config.tr_args.do_eval or eval_config.tr_args.do_predict:    
        if eval_config.tr_args.do_eval:
            results["validation"] = evaluator.validate()
        if eval_config.tr_args.do_predict:
            results["test"] = evaluator.test()
        if os.path.exists(eval_config.tr_args.output_dir):
            subprocess.run(f"rm -r {eval_config.tr_args.output_dir}", shell=True, check=True)
    else:
        print("Evaluation disabled, skipping evaluation")
        exit()

     # Add timestamp to file name to avoid overwriting results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"{eval_config.results_dir}/results_{timestamp}.json"

    # Save results to file
    os.makedirs(eval_config.results_dir, exist_ok=True)
    with open(results_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Results saved at {eval_config.results_dir}")
    print("Evaluation completed")
    exit()



if __name__ == "__main__":
    fire.Fire(main)
