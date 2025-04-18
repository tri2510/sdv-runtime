import { CodeContext } from '../code-converter';
import { PipelineStep } from './pipeline-base';
/**
 * Creates the code snippet which will be put into the velocitas template
 * @extends PipelineStep
 */
export declare class CreateCodeSnippetForTemplateStep extends PipelineStep {
    execute(context: CodeContext): void;
    private changeMemberVariables;
}
