import { CodeContext } from '../code-converter';
import { PipelineStep } from './pipeline-base';
/**
 * Extracts variables from digital.auto prototype to the CodeContext
 * @extends PipelineStep
 */
export declare class ExtractVariablesStep extends PipelineStep {
    execute(context: CodeContext): void;
    private identifyVariables;
    private identifyVariableNames;
    private prepareMemberVariables;
}
