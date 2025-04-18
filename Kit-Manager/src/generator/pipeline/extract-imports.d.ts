import { CodeContext } from '../code-converter';
import { PipelineStep } from './pipeline-base';
/**
 * Extracts imports from digital.auto prototype to the CodeContext
 * @extends PipelineStep
 */
export declare class ExtractImportsStep extends PipelineStep {
    execute(context: CodeContext): void;
    private identifyBasicImports;
}
