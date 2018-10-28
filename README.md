# Using Google Cloud Build, for Continuous Deployment of Hugo powered websites

This repository contains source code for a totally **free** solution for Continuous Deployment of [Hugo][] powered websites, based **entirely** on Google's cloud infrastructure, utilizing Google's [Cloud Build][GCB], [Source Repositories][GCSR], [Registry][GCR], [Key Management Service][GCKMS] and [Firebase][].

## What is Continuous Deployment

Continuous Deployment aims at minimizing the total time taken for code changes in development to deploy in the production environment. In this practice there's no human intervention at all, since the entire pipeline is put into production automatically. This is achieved with appropriate infrastructure capable of automating the steps of testing, building and deploying.

## What is HUGO

[Hugo][] is one of the most popular open-source static site generators. With its amazing speed and flexibility, Hugo makes building websites fun again.

### Hugo Theme

The Hugo theme and content used for the example site is [Coder][] by [Luiz F. A. de Prá][coderAuth]

## How to use the source files

The use of source files is described in the associated post: [Google Cloud Build, CI/CD for Hugo websites][chrisliatas]

## Why is it free

The solution is described as **free**, considering Google's [free tier][Gfree] offering in conjunction with their always free limits and with intended use for personal sites, blogs and in general small scale and limited traffic projects. Please, read carefully Google's Cloud [pricing][GCprice] schemes and be alert for any changes to their free tier offering.


[Hugo]: https://gohugo.io/
[GCB]: https://cloud.google.com/cloud-build/
[GCSR]: https://cloud.google.com/source-repositories/
[GCR]: https://cloud.google.com/container-registry/
[GCKMS]: https://cloud.google.com/kms/
[Firebase]: https://firebase.google.com/
[Gfree]: https://cloud.google.com/free/
[GCprice]: https://cloud.google.com/pricing/
[Coder]: https://themes.gohugo.io/hugo-coder/
[coderAuth]: https://luizdepra.com/
[chrisliatas]: https://liatas.com/posts/hugo-gc-ci-cd/
