import { CodeContext } from '../code-converter';
import { PipelineStep } from './pipeline-base';
/**
 * Prepares digital.auto prototype code snippet to be used to extract all relevant and needed information.
 * @extends PipelineStep
 */
export declare class PrepareCodeSnippetStep extends PipelineStep {
    execute(context: CodeContext): void;
    private removeSubstringsFromArray;
}
