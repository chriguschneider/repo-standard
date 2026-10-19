import type { Dictionary } from './types';

const en: Dictionary = {
  htmlLang: 'en',
  languageName: 'English',
  meta: {
    title: '@@NAME@@',
    description: '@@DESCRIPTION@@',
  },
  previewBanner: 'Preview, not approved',
  nav: {
    home: 'Home',
    languages: 'Language',
  },
  home: {
    heading: '@@NAME@@',
    intro: 'TODO(repo-standard): what visitors find here.',
    postsHeading: 'Posts',
    noPosts: 'No posts yet.',
  },
  post: {
    back: 'Back to the home page',
    draft: 'Draft',
  },
  notFound: {
    title: 'Page not found',
    text: 'This address does not exist (any more).',
    back: 'To the home page',
  },
  footer: {
    source: 'Source',
  },
};

export default en;
