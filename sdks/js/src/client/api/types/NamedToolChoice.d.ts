/**
 * This file was auto-generated by Fern from our API Definition.
 */
import * as JulepApi from "..";
/**
 * Specifies a tool the model should use. Use to force the model to call a specific function.
 */
export interface NamedToolChoice {
    type: "function";
    function: JulepApi.NamedToolChoiceFunction;
}