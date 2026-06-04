export type WordType = "noun" | "verb";
export type Gender = "der" | "die" | "das";
export type Auxiliary = "haben" | "sein";

export interface NounDetails {
  gender: Gender;
  plural: string | null;
}

export interface VerbDetails {
  praeteritum: string;
  perfekt: string;
  auxiliary: Auxiliary;
}

export interface Progress {
  id: number;
  word_id: number;
  ease_factor: number;
  interval_days: number;
  repetitions: number;
  next_review_date: string | null;
  last_reviewed_at: string | null;
  correct_count: number;
  incorrect_count: number;
}

export interface Word {
  id: number;
  german: string;
  translation: string;
  word_type: WordType;
  level: string | null;
  category: string | null;
  example_sentence: string | null;
  noun_detail?: NounDetails | null;
  verb_detail?: VerbDetails | null;
  noun_details?: NounDetails | null;
  verb_details?: VerbDetails | null;
  progress?: Progress | null;
}

export interface CheckAnswerRequest {
  answer: string;
}

export interface CheckAnswerResponse {
  correct: boolean;
  correct_answer: string;
  translation: string;
  message: string;
  word_id: number;
  word_type: WordType;
}
