/* tmda-cgi.c

Copyright (C) 2002 Gre7g Luterman <gre7g@wolfhome.com>

This file is part of TMDA.

TMDA is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.  A copy of this license should
be included in the file COPYING.

TMDA is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License
along with TMDA; if not, write to the Free Software Foundation, Inc.,
59 Temple Place, Suite 330, Boston, MA 02111-1307 USA */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <tmda-cgi.h>

int main(int argc, char *argv[])
{
  int fd;
  putenv("TMDARC=" TMDARC);
  putenv("TMDA_DOMAIN_CONFIG=" TMDA_DOMAIN_CONFIG);
#ifdef AUTH_ARG
  putenv("TMDA_AUTH_TYPE=" AUTH_TYPE);
  putenv("TMDA_AUTH_ARG=" AUTH_ARG);
#endif
  putenv("TMDA_CGI_MODE=" MODE);
  putenv("TMDA_CGI_DISP_DIR=" DISP_DIR);
  putenv("TMDA_BASE_DIR=" BASE_DIR);
#ifdef VLOOKUP
  putenv("TMDA_VUSER=" VUSER);
  putenv("TMDA_VLOOKUP=" VLOOKUP);
#endif
  putenv("TMDA_SESSION_PREFIX=" SESS_PRE);
  putenv("TMDA_SESSION_EXP=" SESS_EXP);
  putenv("TMDA_SESSION_ODDS=" SESS_ODDS);

  fd = open("/dev/null", O_RDONLY);

  if (!chdir(INSTALL))
  {
    execl(PYTHON, PYTHON, "tmda-cgi.py", NULL);
    return 0;
  }
  printf("Content-type: text/html\n\nCannot change to directory: %s", INSTALL);
  return 1;
}
