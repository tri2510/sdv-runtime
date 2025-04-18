import { CodeContext } from '../code-converter';
import { PipelineStep } from './pipeline-base';
/**
 * Extracts methods from digital.auto prototype to the CodeContext
 * @extends PipelineStep
 */
export declare class ExtractMethodsStep extends PipelineStep {
    execute(context: CodeContext): void;
    private identifyMethodBlocks;
    private mapSubscriptionCallbackForVelocitas;
    private changeMemberVariablesInString;
}
