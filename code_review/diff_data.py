# From https://github.com/backstage/backstage/commit/5f0b3a1d4f551acd587b1603a4c0598b057fb6f3.patch/

diff_data = """
From 5f0b3a1d4f551acd587b1603a4c0598b057fb6f3 Mon Sep 17 00:00:00 2001
From: Jamie Klassen <jklassen@vmware.com>
Date: Thu, 17 Nov 2022 16:55:51 -0500
Subject: [PATCH] refactor to use http-proxy-middleware

Signed-off-by: Jamie Klassen <jklassen@vmware.com>
---
 plugins/kubernetes-backend/api-report.md      |  22 +--
 plugins/kubernetes-backend/package.json       |   2 +
 .../src/service/KubernetesBuilder.ts          |  30 ++--
 .../src/service/KubernetesProxy.test.ts       |  91 +++-------
 .../src/service/KubernetesProxy.ts            | 158 +++++++-----------
 yarn.lock                                     |   4 +-
 6 files changed, 117 insertions(+), 190 deletions(-)

diff --git a/plugins/kubernetes-backend/api-report.md b/plugins/kubernetes-backend/api-report.md
index 827ec5e74c6ca..6e0c253f7930b 100644
--- a/plugins/kubernetes-backend/api-report.md
+++ b/plugins/kubernetes-backend/api-report.md
@@ -22,7 +22,7 @@ import { Logger } from 'winston';
 import { Metrics } from '@kubernetes/client-node';
 import type { ObjectsByEntityResponse } from '@backstage/plugin-kubernetes-common';
 import { PluginEndpointDiscovery } from '@backstage/backend-common';
-import type { RequestHandler } from 'express';
+import { RequestHandler } from 'http-proxy-middleware';
 import { TokenCredential } from '@azure/identity';
 
 // @alpha (undocumented)
@@ -195,12 +195,16 @@ export class KubernetesBuilder {
     options: KubernetesObjectsProviderOptions,
   ): KubernetesObjectsProvider;
   // (undocumented)
-  protected buildProxy(): KubernetesProxy;
+  protected buildProxy(
+    logger: Logger,
+    clusterSupplier: KubernetesClustersSupplier,
+  ): KubernetesProxy;
   // (undocumented)
   protected buildRouter(
     objectsProvider: KubernetesObjectsProvider,
     clusterSupplier: KubernetesClustersSupplier,
     catalogApi: CatalogApi,
+    proxy: KubernetesProxy,
   ): express.Router;
   // (undocumented)
   protected buildServiceLocator(
@@ -226,7 +230,10 @@ export class KubernetesBuilder {
   // (undocumented)
   protected getObjectTypesToFetch(): ObjectToFetch[] | undefined;
   // (undocumented)
-  protected getProxy(): KubernetesProxy;
+  protected getProxy(
+    logger: Logger,
+    clusterSupplier: KubernetesClustersSupplier,
+  ): KubernetesProxy;
   // (undocumented)
   protected getServiceLocator(): KubernetesServiceLocator;
   // (undocumented)
@@ -348,14 +355,7 @@ export type KubernetesObjectTypes =
 
 // @alpha (undocumented)
 export class KubernetesProxy {
-  constructor(logger: Logger);
-  // (undocumented)
-  get clustersSupplier(): KubernetesClustersSupplier;
-  set clustersSupplier(clustersSupplier: KubernetesClustersSupplier);
-  // (undocumented)
-  protected readonly logger: Logger;
-  // (undocumented)
-  static readonly PROXY_PATH: string;
+  constructor(logger: Logger, clusterSupplier: KubernetesClustersSupplier);
   // (undocumented)
   proxyRequestHandler: RequestHandler;
 }
diff --git a/plugins/kubernetes-backend/package.json b/plugins/kubernetes-backend/package.json
index d5ab468790e68..9c6cfd0563571 100644
--- a/plugins/kubernetes-backend/package.json
+++ b/plugins/kubernetes-backend/package.json
@@ -56,6 +56,7 @@
     "express-promise-router": "^4.1.0",
     "fs-extra": "10.1.0",
     "helmet": "^6.0.0",
+    "http-proxy-middleware": "^2.0.6",
     "lodash": "^4.17.21",
     "luxon": "^3.0.0",
     "morgan": "^1.10.0",
@@ -67,6 +68,7 @@
   "devDependencies": {
     "@backstage/cli": "workspace:^",
     "@types/aws4": "^1.5.1",
+    "@types/http-proxy-middleware": "^0.19.3",
     "aws-sdk-mock": "^5.2.1",
     "msw": "^0.48.0",
     "supertest": "^6.1.3"
diff --git a/plugins/kubernetes-backend/src/service/KubernetesBuilder.ts b/plugins/kubernetes-backend/src/service/KubernetesBuilder.ts
index 3ac27decc8a60..a5e67ebe2ab98 100644
--- a/plugins/kubernetes-backend/src/service/KubernetesBuilder.ts
+++ b/plugins/kubernetes-backend/src/service/KubernetesBuilder.ts
@@ -108,11 +108,9 @@ export class KubernetesBuilder {
 
     const fetcher = this.getFetcher();
 
-    const proxy = this.getProxy();
-
     const clusterSupplier = this.getClusterSupplier();
 
-    proxy.clustersSupplier = clusterSupplier;
+    const proxy = this.getProxy(logger, clusterSupplier);
 
     const serviceLocator = this.getServiceLocator();
 
@@ -128,6 +126,7 @@ export class KubernetesBuilder {
       objectsProvider,
       clusterSupplier,
       this.env.catalogApi,
+      proxy,
     );
 
     return {
@@ -252,8 +251,11 @@ export class KubernetesBuilder {
     throw new Error('not implemented');
   }
 
-  protected buildProxy(): KubernetesProxy {
-    this.proxy = new KubernetesProxy(this.env.logger);
+  protected buildProxy(
+    logger: Logger,
+    clusterSupplier: KubernetesClustersSupplier,
+  ): KubernetesProxy {
+    this.proxy = new KubernetesProxy(logger, clusterSupplier);
     return this.proxy;
   }
 
@@ -261,13 +263,12 @@ export class KubernetesBuilder {
     objectsProvider: KubernetesObjectsProvider,
     clusterSupplier: KubernetesClustersSupplier,
     catalogApi: CatalogApi,
+    proxy: KubernetesProxy,
   ): express.Router {
     const logger = this.env.logger;
     const router = Router();
     router.use(express.json());
 
-    const proxy = this.getProxy();
-
     // @deprecated
     router.post('/services/:serviceId', async (req, res) => {
       const serviceId = req.params.serviceId;
@@ -298,13 +299,7 @@ export class KubernetesBuilder {
       });
     });
 
-    if (typeof proxy?.proxyRequestHandler === 'function') {
-      router.get(KubernetesProxy.PROXY_PATH, proxy.proxyRequestHandler);
-      router.post(KubernetesProxy.PROXY_PATH, proxy.proxyRequestHandler);
-      router.put(KubernetesProxy.PROXY_PATH, proxy.proxyRequestHandler);
-      router.patch(KubernetesProxy.PROXY_PATH, proxy.proxyRequestHandler);
-      router.delete(KubernetesProxy.PROXY_PATH, proxy.proxyRequestHandler);
-    }
+    router.use('/proxy', proxy.proxyRequestHandler);
 
     addResourceRoutesToRouter(router, catalogApi, objectsProvider);
 
@@ -384,7 +379,10 @@ export class KubernetesBuilder {
     return objectTypesToFetch;
   }
 
-  protected getProxy() {
-    return this.proxy ?? this.buildProxy();
+  protected getProxy(
+    logger: Logger,
+    clusterSupplier: KubernetesClustersSupplier,
+  ) {
+    return this.proxy ?? this.buildProxy(logger, clusterSupplier);
   }
 }
diff --git a/plugins/kubernetes-backend/src/service/KubernetesProxy.test.ts b/plugins/kubernetes-backend/src/service/KubernetesProxy.test.ts
index a72681fc7365d..5d4eaa795b2bb 100644
--- a/plugins/kubernetes-backend/src/service/KubernetesProxy.test.ts
+++ b/plugins/kubernetes-backend/src/service/KubernetesProxy.test.ts
@@ -16,12 +16,14 @@
 import 'buffer';
 
 import { getVoidLogger } from '@backstage/backend-common';
-import { setupRequestMockHandlers } from '@backstage/backend-test-utils';
 import { NotFoundError } from '@backstage/errors';
 import { getMockReq, getMockRes } from '@jest-mock/express';
-import { Request } from 'express';
+import type { Request } from 'express';
+import express from 'express';
+import request from 'supertest';
 import { rest } from 'msw';
 import { setupServer } from 'msw/node';
+import { setupRequestMockHandlers } from '@backstage/backend-test-utils';
 
 import { ClusterDetails, KubernetesClustersSupplier } from '../types/types';
 import {
@@ -33,6 +35,7 @@ import {
 describe('KubernetesProxy', () => {
   let proxy: KubernetesProxy;
   const worker = setupServer();
+
   setupRequestMockHandlers(worker);
 
   const buildMockRequest = (clusterName: any, path: string): Request => {
@@ -58,20 +61,17 @@ describe('KubernetesProxy', () => {
     return req;
   };
 
-  const buildClustersSupplierWithClusters = (
-    clusters: ClusterDetails[],
-  ): KubernetesClustersSupplier => ({
-    getClusters: async () => {
-      return clusters;
-    },
-  });
+  const clusterSupplier: jest.Mocked<KubernetesClustersSupplier> = {
+    getClusters: jest.fn(),
+  };
 
   beforeEach(() => {
-    proxy = new KubernetesProxy(getVoidLogger());
+    jest.resetAllMocks();
+    proxy = new KubernetesProxy(getVoidLogger(), clusterSupplier);
   });
 
   it('should return a ERROR_NOT_FOUND if no clusters are found', async () => {
-    proxy.clustersSupplier = buildClustersSupplierWithClusters([]);
+    clusterSupplier.getClusters.mockResolvedValue([]);
 
     const req = buildMockRequest('test', 'api');
     const { res, next } = getMockRes();
@@ -81,22 +81,7 @@ describe('KubernetesProxy', () => {
     );
   });
 
-  it('should match the response code of the Kubernetes response', async () => {
-    const clusters: ClusterDetails[] = [
-      {
-        name: 'cluster1',
-        url: 'https://localhost:9999',
-        serviceAccountToken: 'token',
-        authProvider: 'serviceAccount',
-        skipTLSVerify: true,
-      },
-    ];
-
-    proxy.clustersSupplier = buildClustersSupplierWithClusters(clusters);
-
-    const req = buildMockRequest('cluster1', 'api');
-    const { res: response, next } = getMockRes();
-
+  it('should pass the exact response from Kubernetes', async () => {
     const apiResponse = {
       kind: 'APIVersions',
       versions: ['v1'],
@@ -108,54 +93,28 @@ describe('KubernetesProxy', () => {
       ],
     };
 
-    worker.use(
-      rest.get(`${clusters[0].url}/${req.params.path}`, (_, res, ctx) =>
-        res(ctx.status(299), ctx.body(JSON.stringify(apiResponse))),
-      ),
-    );
-
-    await proxy.proxyRequestHandler(req, response, next);
-
-    expect(response.status).toHaveBeenCalledWith(299);
-    expect(response.json).toHaveBeenCalledWith(apiResponse);
-  });
-
-  it('should pass the exact response data from Kubernetes', async () => {
-    const clusters: ClusterDetails[] = [
+    clusterSupplier.getClusters.mockResolvedValue([
       {
         name: 'cluster1',
         url: 'https://localhost:9999',
-        serviceAccountToken: 'token',
+        serviceAccountToken: '',
         authProvider: 'serviceAccount',
-        skipTLSVerify: true,
       },
-    ];
-
-    proxy.clustersSupplier = buildClustersSupplierWithClusters(clusters);
-
-    const req = buildMockRequest('cluster1', 'api');
-    const { res: response, next } = getMockRes();
-
-    const apiResponse = {
-      kind: 'APIVersions',
-      versions: ['v1'],
-      serverAddressByClientCIDRs: [
-        {
-          clientCIDR: '0.0.0.0/0',
-          serverAddress: '192.168.0.1:3333',
-        },
-      ],
-    };
-
+    ] as ClusterDetails[]);
+    const app = express().use('/mountpath', proxy.proxyRequestHandler);
+    const requestPromise = request(app)
+      .get('/mountpath/api')
+      .set(HEADER_KUBERNETES_CLUSTER, 'cluster1');
     worker.use(
-      rest.get(`${clusters[0].url}/${req.params.path}`, (_, res, ctx) =>
-        res(ctx.status(200), ctx.body(JSON.stringify(apiResponse))),
+      rest.get('https://localhost:9999/api', (_, res, ctx) =>
+        res(ctx.status(299), ctx.json(apiResponse)),
       ),
+      rest.all(requestPromise.url, (req, _res, _ctx) => req.passthrough()),
     );
 
-    await proxy.proxyRequestHandler(req, response, next);
+    const response = await requestPromise;
 
-    expect(response.status).toHaveBeenCalledWith(200);
-    expect(response.json).toHaveBeenCalledWith(apiResponse);
+    expect(response.status).toEqual(299);
+    expect(response.body).toStrictEqual(apiResponse);
   });
 });
diff --git a/plugins/kubernetes-backend/src/service/KubernetesProxy.ts b/plugins/kubernetes-backend/src/service/KubernetesProxy.ts
index 92f3c0ea6c690..7cc3a974167c9 100644
--- a/plugins/kubernetes-backend/src/service/KubernetesProxy.ts
+++ b/plugins/kubernetes-backend/src/service/KubernetesProxy.ts
@@ -13,21 +13,19 @@
  * See the License for the specific language governing permissions and
  * limitations under the License.
  */
-import {
-  AuthenticationError,
-  ConflictError,
-  ForwardedError,
-  InputError,
-  NotFoundError,
-} from '@backstage/errors';
-import { bufferFromFileOrString, KubeConfig } from '@kubernetes/client-node';
-import * as https from 'https';
-import fetch, { RequestInit, Response } from 'node-fetch';
+import { ForwardedError, InputError, NotFoundError } from '@backstage/errors';
+import { bufferFromFileOrString } from '@kubernetes/client-node';
 import { Logger } from 'winston';
+import { ErrorResponseBody, serializeError } from '@backstage/errors';
 
 import { ClusterDetails, KubernetesClustersSupplier } from '../types/types';
 
-import type { Request as ExpressRequest, RequestHandler } from 'express';
+import type { Request } from 'express';
+import {
+  RequestHandler,
+  Options,
+  createProxyMiddleware,
+} from 'http-proxy-middleware';
 
 /**
  *
@@ -41,52 +39,66 @@ export const APPLICATION_JSON: string = 'application/json';
  */
 export const HEADER_KUBERNETES_CLUSTER: string = 'X-Kubernetes-Cluster';
 
-const HEADER_CONTENT_TYPE: string = 'Content-Type';
-
-const CLUSTER_USER_NAME: string = 'backstage';
-
 /**
  *
  * @alpha
  */
 export class KubernetesProxy {
-  private _clustersSupplier?: KubernetesClustersSupplier;
+  constructor(
+    private readonly logger: Logger,
+    private readonly clusterSupplier: KubernetesClustersSupplier,
+  ) {}
 
-  static readonly PROXY_PATH: string = '/proxy/:path(*)';
-
-  constructor(protected readonly logger: Logger) {}
-
-  public proxyRequestHandler: RequestHandler = async (req, res) => {
+  public proxyRequestHandler: RequestHandler = async (req, res, next) => {
     const requestedCluster = this.getKubernetesRequestedCluster(req);
 
     const clusterDetails = await this.getClusterDetails(requestedCluster);
 
-    const response = await this.makeRequestToCluster(clusterDetails, req);
-
-    const data = await response.text();
-
-    res.status(response.status).send(data);
+    const clusterUrl = new URL(clusterDetails.url);
+    const options = {
+      logProvider: () => this.logger,
+      secure: !clusterDetails.skipTLSVerify,
+      target: {
+        protocol: clusterUrl.protocol,
+        host: clusterUrl.hostname,
+        port: clusterUrl.port,
+        ca: bufferFromFileOrString('', clusterDetails.caData)?.toString(),
+      },
+      pathRewrite: { [`^${req.baseUrl}`]: '' },
+      onError: (error: Error) => {
+        const wrappedError = new ForwardedError(
+          `Cluster '${requestedCluster}' request error`,
+          error,
+        );
+
+        this.logger.error(wrappedError);
+
+        const body: ErrorResponseBody = {
+          error: serializeError(wrappedError, {
+            includeStack: process.env.NODE_ENV === 'development',
+          }),
+          request: { method: req.method, url: req.originalUrl },
+          response: { statusCode: 500 },
+        };
+
+        res.status(500).json(body);
+      },
+    } as Options;
+
+    // Probably too risky without permissions protecting this endpoint
+    // if (clusterDetails.serviceAccountToken) {
+    //   options.headers = {
+    //     Authorization: `Bearer ${clusterDetails.serviceAccountToken}`,
+    //   };
+    // }
+    createProxyMiddleware(options)(req, res, next);
   };
 
-  public get clustersSupplier(): KubernetesClustersSupplier {
-    if (this._clustersSupplier ? false : this._clustersSupplier ?? true) {
-      throw new ConflictError("Missing Proxy's Clusters Supplier");
-    }
-
-    return this._clustersSupplier as KubernetesClustersSupplier;
-  }
-
-  public set clustersSupplier(clustersSupplier) {
-    this._clustersSupplier = clustersSupplier;
-  }
-
-  private getKubernetesRequestedCluster(req: ExpressRequest): string {
-    const requestedClusterName: string =
-      req.header(HEADER_KUBERNETES_CLUSTER) ?? '';
+  private getKubernetesRequestedCluster(req: Request): string {
+    const requestedClusterName = req.header(HEADER_KUBERNETES_CLUSTER);
 
     if (!requestedClusterName) {
-      this.logger.error(`Malformed ${HEADER_KUBERNETES_CLUSTER} header.`);
-      throw new InputError(`Malformed ${HEADER_KUBERNETES_CLUSTER} header.`);
+      throw new InputError(`Missing '${HEADER_KUBERNETES_CLUSTER}' header.`);
     }
 
     return requestedClusterName;
@@ -95,62 +107,16 @@ export class KubernetesProxy {
   private async getClusterDetails(
     requestedCluster: string,
   ): Promise<ClusterDetails> {
-    const clusters = await this.clustersSupplier.getClusters();
+    const clusters = await this.clusterSupplier.getClusters();
 
-    const clusterDetail = clusters.find(cluster =>
-      requestedCluster.includes(cluster.name),
+    const clusterDetail = clusters.find(
+      cluster => cluster.name === requestedCluster,
     );
 
-    if (clusterDetail ? false : clusterDetail ?? true) {
-      this.logger.error(
-        `Cluster ${requestedCluster} details not found in config`,
-      );
-
-      throw new NotFoundError("Cluster's detail not found");
+    if (!clusterDetail) {
+      throw new NotFoundError(`Cluster '${requestedCluster}' not found`);
     }
 
-    return clusterDetail as ClusterDetails;
+    return clusterDetail;
   }
-
-  private async makeRequestToCluster(
-    details: ClusterDetails,
-    req: ExpressRequest,
-  ): Promise<Response> {
-    const serverURI = details.url;
-
-    const path = decodeURIComponent(req.params.path) || '';
-    const uri = `${serverURI}/${path}`;
-
-    return await this.sendClusterRequest(details, uri, req);
-  }
-
-  private async sendClusterRequest(
-    details: ClusterDetails,
-    uri: string,
-    req: ExpressRequest,
-  ): Promise<Response> {
-    const { method, headers, body } = req;
-
-    const reqData: RequestInit = {
-      method,
-      headers: headers as { [key: string]: string },
-    };
-
-    if (details.skipTLSVerify) {
-      reqData.agent = new https.Agent({ rejectUnauthorized: false });
-    } else if (details.caData) {
-      const ca = bufferFromFileOrString('', details.caData)?.toString() || '';
-      reqData.agent = new https.Agent({ ca });
-    }
-
-    if (body && Object.keys(body).length > 0) {
-      reqData.body = JSON.stringify(body);
-    }
-
-    try {
-      return fetch(uri, reqData);
-    } catch (e: any) {
-      throw new ForwardedError(`Cluster ${details.name} request error`, e);
-    }
-  }
-
+}
diff --git a/yarn.lock b/yarn.lock
index 653eeec7ceae6..b049053f9e95c 100644
--- a/yarn.lock
+++ b/yarn.lock
@@ -5977,6 +5977,7 @@ __metadata:
     "@kubernetes/client-node": 0.17.0
     "@types/aws4": ^1.5.1
     "@types/express": ^4.17.6
+    "@types/http-proxy-middleware": ^0.19.3
     "@types/luxon": ^3.0.0
     aws-sdk: ^2.840.0
     aws-sdk-mock: ^5.2.1
@@ -5987,6 +5988,7 @@ __metadata:
     express-promise-router: ^4.1.0
     fs-extra: 10.1.0
     helmet: ^6.0.0
+    http-proxy-middleware: ^2.0.6
     lodash: ^4.17.21
     luxon: ^3.0.0
     morgan: ^1.10.0
@@ -23361,7 +23363,7 @@ __metadata:
   languageName: node
   linkType: hard
 
-"http-proxy-middleware@npm:^2.0.0, http-proxy-middleware@npm:^2.0.3":
+"http-proxy-middleware@npm:^2.0.0, http-proxy-middleware@npm:^2.0.3, http-proxy-middleware@npm:^2.0.6":
   version: 2.0.6
   resolution: "http-proxy-middleware@npm:2.0.6"
   dependencies:"""
