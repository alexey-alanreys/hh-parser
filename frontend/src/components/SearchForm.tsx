import type { FormEvent } from 'react';
import { useState } from 'react';

import type { Experience, ScanRequest } from '../types';

interface Props {
  disabled: boolean;
  onSubmit: (payload: ScanRequest) => void;
}

const EXPERIENCE_OPTIONS: { value: Experience | ''; label: string }[] = [
  { value: '', label: 'Любой опыт' },
  { value: 'noExperience', label: 'Без опыта' },
  { value: 'between1And3', label: '1–3 года' },
  { value: 'between3And6', label: '3–6 лет' },
  { value: 'moreThan6', label: '6+ лет' },
];

export default function SearchForm({
  disabled,
  onSubmit,
}: Props): React.JSX.Element {
  const [query, setQuery] = useState('QA Automation Python');
  const [experience, setExperience] = useState<Experience | ''>('');
  const [maxVacancies, setMaxVacancies] = useState(50);
  const [touched, setTouched] = useState(false);

  const queryTooShort = query.trim().length < 2;

  function handleSubmit(e: FormEvent): void {
    e.preventDefault();
    setTouched(true);
    if (queryTooShort || disabled) return;
    onSubmit({
      query: query.trim(),
      experience: experience || null,
      max_vacancies: maxVacancies,
    });
  }

  return (
    <form
      className='search-form'
      onSubmit={handleSubmit}
    >
      <div className='field field-grow'>
        <label htmlFor='query'>Вакансия</label>
        <input
          disabled={disabled}
          id='query'
          placeholder='Frontend React'
          type='text'
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        {touched && queryTooShort && (
          <span className='field-error'>Минимум 2 символа</span>
        )}
      </div>

      <div className='field'>
        <label htmlFor='experience'>Опыт</label>
        <select
          disabled={disabled}
          id='experience'
          value={experience}
          onChange={(e) => setExperience(e.target.value as Experience | '')}
        >
          {EXPERIENCE_OPTIONS.map((opt) => (
            <option
              key={opt.value}
              value={opt.value}
            >
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className='field field-narrow'>
        <label htmlFor='max_vacancies'>Вакансий</label>
        <input
          disabled={disabled}
          id='max_vacancies'
          max={500}
          min={1}
          type='number'
          value={maxVacancies}
          onChange={(e) => setMaxVacancies(Number(e.target.value))}
        />
      </div>

      <button
        className='btn-primary'
        disabled={disabled}
        type='submit'
      >
        {disabled ? 'Идёт сканирование…' : 'Сканировать'}
      </button>
    </form>
  );
}
