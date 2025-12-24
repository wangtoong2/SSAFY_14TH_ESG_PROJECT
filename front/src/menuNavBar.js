import {
  mdiAccount,
  mdiCogOutline,
  mdiEmail,
  mdiLogout,
  mdiThemeLightDark,
  mdiMenu,
  mdiViewList,
} from '@mdi/js'

import { useAccountStore } from '@/stores/accounts'

export default [
  {
    icon: mdiThemeLightDark,
    isToggleLightDark: true,
  },
  {
    icon: mdiMenu,
    label: 'Menu',
    menu: [
      { icon: mdiAccount, label: '프로필', to: '/profile' },
      { icon: mdiViewList, label: '내 관심기업', to: '/favorites' },
      { isDivider: true },
      { icon: mdiLogout, label: '로그아웃', isLogout: true },
    ],
    // mark this as the right-side hamburger so navbar item can style it specially
    isRightHamburger: true,
  },
]




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
