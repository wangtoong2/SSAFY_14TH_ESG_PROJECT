import {
  mdiAccount,
  mdiCommentTextOutline,
  mdiFileDocumentOutline,
  mdiLogout,
  mdiThemeLightDark,
  mdiMenu,
  mdiViewList,
  mdiLogin,
  mdiAccountPlus,
} from '@mdi/js'

export const buildMenuNavBar = (isLogin) => [
  {
    icon: mdiThemeLightDark,
    isToggleLightDark: true,
  },
  {
    icon: mdiMenu,
    label: 'Menu',
    menu: isLogin
      ? [
          { icon: mdiAccount, label: '프로필', to: '/profile/edit' },
          { icon: mdiViewList, label: '내 관심기업', to: '/favorites' },
          { icon: mdiFileDocumentOutline, label: '내가 작성한 글', to: '/my/articles' },
          { icon: mdiCommentTextOutline, label: '내가 작성한 댓글', to: '/my/comments' },
          { isDivider: true },
          { icon: mdiLogout, label: '로그아웃', isLogout: true },
        ]
      : [
          { icon: mdiLogin, label: '로그인', to: '/login' },
          { icon: mdiAccountPlus, label: '회원가입', to: '/signup' },
        ],
    // mark this as the right-side hamburger so navbar item can style it specially
    isRightHamburger: true,
  },
]

export default buildMenuNavBar




// 기존 작성된 코드
// export default [
  // {
  //   icon: mdiMenu,
  //   label: 'Menu',
  //   menu: [
  //     {
  //       icon: mdiClockOutline,
  //       label: 'Item One',
  //     },
  //     {
  //       icon: mdiCloud,
  //       label: 'Item Two',
  //     },
  //     {
  //       isDivider: true,
  //     },
  //     {
  //       icon: mdiCrop,
  //       label: 'Item Last',
  //     },
  //   ],
  // },
//   {
//     isCurrentUser: true,
//     menu: [
//       {
//         icon: mdiAccount,
//         label: 'My Profile',
//         to: '/profile',
//       },
//       {
//         icon: mdiCogOutline,
//         label: 'Settings',
//       },
//       {
//         icon: mdiEmail,
//         label: 'Messages',
//       },
//       {
//         isDivider: true,
//       },
//       {
//         icon: mdiLogout,
//         label: 'Log Out',
//         isLogout: true,
//       },
//     ],
//   },
//   {
//     icon: mdiThemeLightDark,
//     label: 'Light/Dark',
//     isDesktopNoLabel: true,
//     isToggleLightDark: true,
//   },
//   {
//     icon: mdiLogout,
//     label: 'Log out',
//     isDesktopNoLabel: true,
//     isLogout: true,
//   },
// ]
