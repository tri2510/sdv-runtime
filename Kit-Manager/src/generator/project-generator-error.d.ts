import { AxiosError } from 'axios';
/**
 * ProjectGeneratorError puts all relevant information together
 *
 * @property {string} error.name                          - Name of the error.
 * @property {string} error.message                       - Error message.
 * @property {number | undefined} error.statusCode        - API response status code.
 * @property {string | undefined} error.statusText        - API response status text.
 * @property {string[] | undefined} error.responseMessage - Contains API response messages if available.
 */
export declare class ProjectGeneratorError extends AxiosError {
    statusCode: number | undefined;
    statusText: string | undefined;
    responseMessages: string[] | undefined;
    constructor(error: AxiosError);
}
