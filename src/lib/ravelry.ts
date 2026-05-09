export interface RavelryPatternData {
  yarnWeight: string | null;
  wpi: string | null;
  sizes: string | null;
  gauge: string | null;
  needleSizes: string[];
  yardage: string | null;
  languages: string[];
  rating: number | null;
  ratingCount: number | null;
  difficulty: number | null;
  notes: string | null;
  permalink: string;
}

export async function fetchPatternData(ravelryUrl: string): Promise<RavelryPatternData | null> {
  const username = import.meta.env.RAVELRY_USERNAME;
  const apiKey = import.meta.env.RAVELRY_API_KEY;
  if (!username || !apiKey) return null;

  const match = ravelryUrl.match(/\/patterns\/library\/([^/?#]+)/);
  if (!match) return null;
  const permalink = match[1];

  try {
    const res = await fetch(
      `https://api.ravelry.com/patterns/show.json?permalink=${permalink}`,
      { headers: { Authorization: `Basic ${btoa(`${username}:${apiKey}`)}` } }
    );
    if (!res.ok) return null;
    const json = await res.json();
    const p = json.pattern;

    const needleSizes: string[] = (p.pattern_needle_sizes ?? [])
      .filter((n: any) => n.knitting)
      .map((n: any) => n.name.trim());

    const languages: string[] = (p.languages ?? []).map((l: any) => l.name);

    const notes = p.notes
      ? p.notes.replace(/\s+/g, ' ').trim().slice(0, 280) + (p.notes.length > 280 ? '…' : '')
      : null;

    return {
      yarnWeight: p.yarn_weight_description ?? p.yarn_weight?.name ?? null,
      wpi: p.yarn_weight?.wpi ?? null,
      sizes: p.sizes_available ?? null,
      gauge: p.gauge_description ?? null,
      needleSizes,
      yardage: p.yardage_description ?? null,
      languages,
      rating: p.rating_count > 0 ? p.rating_average : null,
      ratingCount: p.rating_count > 0 ? p.rating_count : null,
      difficulty: p.difficulty_count > 0 ? p.difficulty_average : null,
      notes,
      permalink,
    };
  } catch {
    return null;
  }
}
