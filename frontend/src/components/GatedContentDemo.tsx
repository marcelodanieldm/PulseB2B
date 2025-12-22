/**
 * Gated Content Demo Component
 * Visual example of all gating patterns
 */

'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { GatedContent, GatedTableCell, GatedInline } from '@/components/GatedContent';
import { UnlockPremiumModal } from '@/components/UnlockPremiumModal';
import { Mail, Phone, DollarSign, Lock, Unlock } from 'lucide-react';

export function GatedContentDemo() {
  const [isPremium, setIsPremium] = useState(false);
  const [showModal, setShowModal] = useState(false);

  return (
    <div className="min-h-screen bg-gray-950 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Gated Content Demo
            </h1>
            <p className="text-gray-400">
              Toggle premium status to see gating behavior
            </p>
          </div>
          <Button
            onClick={() => setIsPremium(!isPremium)}
            variant={isPremium ? "default" : "outline"}
            className="gap-2"
          >
            {isPremium ? <Unlock className="w-4 h-4" /> : <Lock className="w-4 h-4" />}
            {isPremium ? "Premium Active" : "Free User"}
          </Button>
        </div>

        {/* Status Badge */}
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${isPremium ? 'bg-green-500' : 'bg-gray-500'} animate-pulse`}></div>
                <span className="text-white">
                  Current Status: <Badge variant={isPremium ? "default" : "secondary"}>{isPremium ? "Premium" : "Free"}</Badge>
                </span>
              </div>
              {!isPremium && (
                <Button
                  onClick={() => setShowModal(true)}
                  size="sm"
                  className="bg-gradient-to-r from-amber-500 to-orange-500"
                >
                  Upgrade to Premium
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Pattern 1: GatedContent Wrapper */}
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Mail className="w-5 h-5 text-blue-500" />
                Pattern 1: Full Blur Overlay
              </CardTitle>
              <CardDescription>
                Best for larger content blocks with centered unlock button
              </CardDescription>
            </CardHeader>
            <CardContent>
              <GatedContent
                isLocked={!isPremium}
                onUnlock={() => setShowModal(true)}
                showButton={true}
                buttonText="Unlock Email"
              >
                <div className="p-4 bg-gray-950 rounded-lg border border-gray-800">
                  <div className="flex items-center gap-3">
                    <Mail className="w-8 h-8 text-blue-500" />
                    <div>
                      <p className="text-sm text-gray-400">Contact Email</p>
                      <a href="mailto:ceo@techcorp.com" className="text-blue-400 hover:underline">
                        ceo@techcorp.com
                      </a>
                    </div>
                  </div>
                </div>
              </GatedContent>
            </CardContent>
          </Card>

          {/* Pattern 2: GatedTableCell */}
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Phone className="w-5 h-5 text-green-500" />
                Pattern 2: Table Cell Hover
              </CardTitle>
              <CardDescription>
                Best for table columns - unlock button appears on hover
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="border border-gray-800 rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-800 bg-gray-950">
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">
                        Phone Number
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-gray-800 hover:bg-gray-950">
                      <td className="px-4 py-3">
                        <GatedTableCell
                          value={
                            <a href="tel:+14155551234" className="text-green-400 hover:underline">
                              +1 (415) 555-1234
                            </a>
                          }
                          isLocked={!isPremium}
                          onUnlock={() => setShowModal(true)}
                          placeholder="+1 (•••) •••-••••"
                        />
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Pattern 3: GatedInline */}
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-amber-500" />
                Pattern 3: Inline Text Lock
              </CardTitle>
              <CardDescription>
                Best for inline text with subtle lock icon indicator
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="p-4 bg-gray-950 rounded-lg border border-gray-800">
                <p className="text-white mb-2">
                  Company raised{" "}
                  <GatedInline
                    value="$50M Series B"
                    isLocked={!isPremium}
                    onUnlock={() => setShowModal(true)}
                    showIcon={true}
                  />
                  {" "}in funding last month.
                </p>
                <p className="text-xs text-gray-500">
                  Click the blurred text or lock icon to unlock
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Real-world example */}
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="text-white">
                Real-World Example
              </CardTitle>
              <CardDescription>
                Company profile card with multiple gated fields
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-gray-950 rounded-lg border border-gray-800">
                  <span className="text-sm text-gray-400">Email:</span>
                  <GatedInline
                    value="hiring@company.com"
                    isLocked={!isPremium}
                    onUnlock={() => setShowModal(true)}
                  />
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-950 rounded-lg border border-gray-800">
                  <span className="text-sm text-gray-400">Phone:</span>
                  <GatedInline
                    value="+1 (555) 987-6543"
                    isLocked={!isPremium}
                    onUnlock={() => setShowModal(true)}
                  />
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-950 rounded-lg border border-gray-800">
                  <span className="text-sm text-gray-400">Funding:</span>
                  <GatedInline
                    value="$25.5M Series A"
                    isLocked={!isPremium}
                    onUnlock={() => setShowModal(true)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Implementation Code */}
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader>
            <CardTitle className="text-white">Implementation Example</CardTitle>
            <CardDescription>
              Copy this code to use gated content in your components
            </CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="bg-gray-950 p-4 rounded-lg overflow-x-auto text-xs">
              <code className="text-gray-300">
{`import { GatedTableCell } from '@/components/GatedContent';
import { useAuth } from '@/hooks/useAuth';

export function MyTable() {
  const { isPremium } = useAuth();
  const [showModal, setShowModal] = useState(false);

  return (
    <table>
      <tr>
        <td>
          <GatedTableCell
            value={<a href="mailto:email">email@company.com</a>}
            isLocked={!isPremium}
            onUnlock={() => setShowModal(true)}
            placeholder="•••@company.com"
          />
        </td>
      </tr>
    </table>
  );
}`}
              </code>
            </pre>
          </CardContent>
        </Card>
      </div>

      {/* Unlock Premium Modal */}
      <UnlockPremiumModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        stripePaymentLink="https://buy.stripe.com/test_demo"
      />
    </div>
  );
}
