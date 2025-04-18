import { CodeContext } from '../code-converter';
import { PipelineStep } from './pipeline-base';
/**
 * Extracts classes from digital.auto prototype to the CodeContext
 * @extends PipelineStep
 */
export declare class ExtractClassesStep extends PipelineStep {
    execute(context: CodeContext): void;
    private identifySeperateClass;
    private lineBelongsToClass;
}
