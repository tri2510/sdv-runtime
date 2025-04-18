"use strict";
// Copyright (c) 2022 Robert Bosch GmbH
//
// This program and the accompanying materials are made available under the
// terms of the Apache License, Version 2.0 which is available at
// https://www.apache.org/licenses/LICENSE-2.0.
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations
// under the License.
//
// SPDX-License-Identifier: Apache-2.0
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProjectGeneratorError = void 0;
const axios_1 = require("axios");
/**
 * ProjectGeneratorError puts all relevant information together
 *
 * @property {string} error.name                          - Name of the error.
 * @property {string} error.message                       - Error message.
 * @property {number | undefined} error.statusCode        - API response status code.
 * @property {string | undefined} error.statusText        - API response status text.
 * @property {string[] | undefined} error.responseMessage - Contains API response messages if available.
 */
class ProjectGeneratorError extends axios_1.AxiosError {
    constructor(error) {
        var _a, _b, _c, _d;
        const errors = ((_a = error.response) === null || _a === void 0 ? void 0 : _a.data).errors;
        super(error.message);
        this.name = 'ProjectGeneratorError';
        this.statusCode = (_b = error.response) === null || _b === void 0 ? void 0 : _b.status;
        this.statusText = (_c = error.response) === null || _c === void 0 ? void 0 : _c.statusText;
        this.responseMessages = errors ? errors : ((_d = error.response) === null || _d === void 0 ? void 0 : _d.data).message;
    }
}
exports.ProjectGeneratorError = ProjectGeneratorError;
