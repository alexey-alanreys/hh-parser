import type { CountItem } from '../types';

interface Props {
  title: string;
  items: CountItem[];
}

export default function RankedList({
  title,
  items,
}: Props): React.JSX.Element {
  const max = items.length > 0 ? (items[0]?.count ?? 1) : 1;

  return (
    <section className='ranked-list'>
      <h2>{title}</h2>
      {items.length === 0 ? (
        <p className='empty-note'>
          Нет результатов выше порога — попробуйте увеличить число вакансий.
        </p>
      ) : (
        <ol>
          {items.map((item, i) => (
            <li
              key={item.label}
              className='ranked-row'
            >
              <span className='rank'>{String(i + 1).padStart(2, '0')}</span>
              <span className='rank-label'>{item.label}</span>
              <span className='rank-bar-track'>
                <span
                  className='rank-bar-fill'
                  style={{ width: `${(item.count / max) * 100}%` }}
                />
              </span>
              <span className='rank-count'>{item.count}</span>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
